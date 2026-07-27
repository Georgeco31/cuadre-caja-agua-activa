param(
    [string]$BackupPath = "",
    [switch]$KeepContainer
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ComposeFile = "docker-compose.prod.yml"
$EnvFile = ".env.production.local"
$BackupDirectory = Join-Path $RepoRoot "backups/postgres"
$EvidenceRelativeDirectory = "backups/restore-tests"
$EvidenceDirectory = Join-Path $RepoRoot $EvidenceRelativeDirectory
$ExpectedAlembicVersion = "0026_user_roles"
$ExpectedTables = @(
    "users",
    "cash_sessions",
    "denominations",
    "cash_count_items",
    "expenses",
    "correction_logs",
    "customers",
    "products",
    "employees",
    "delivery_routes",
    "vehicles",
    "purchases",
    "payroll_runs"
)

. (Join-Path $PSScriptRoot "prod-local-common.ps1")

function Get-SafeProductionHealth {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ComposeFile,

        [Parameter(Mandatory = $true)]
        [string]$EnvFile
    )

    $serviceStatuses = @()
    $containerIds = @{}

    foreach ($service in @("db", "api", "web")) {
        $idLines = @(
            & docker compose -f $ComposeFile --env-file $EnvFile `
                ps -q $service 2>$null
        )
        if ($LASTEXITCODE -ne 0 -or $idLines.Count -eq 0) {
            throw "El servicio productivo $service no esta creado."
        }

        $containerId = ([string]($idLines | Select-Object -Last 1)).Trim()
        if ([string]::IsNullOrWhiteSpace($containerId)) {
            throw "El servicio productivo $service no tiene contenedor."
        }
        $containerIds[$service] = $containerId

        $stateLines = @(
            & docker inspect --format `
                '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}not_configured{{end}}' `
                $containerId 2>$null
        )
        if ($LASTEXITCODE -ne 0 -or $stateLines.Count -eq 0) {
            throw "No se pudo inspeccionar el servicio productivo $service."
        }

        $stateParts = ([string]($stateLines | Select-Object -Last 1)).Trim().Split("|")
        if ($stateParts.Count -ne 2) {
            throw "Docker devolvio un estado inesperado para $service."
        }

        $state = $stateParts[0]
        $health = $stateParts[1]
        if ($state -ne "running" -or $health -ne "healthy") {
            throw "El servicio productivo $service no esta healthy (state=$state, health=$health)."
        }

        $serviceStatuses += [PSCustomObject][ordered]@{
            service = $service
            state = $state
            health = $health
        }
    }

    $portBindingLines = @(
        & docker inspect --format '{{json .HostConfig.PortBindings}}' `
            $containerIds["db"] 2>$null
    )
    if ($LASTEXITCODE -ne 0 -or $portBindingLines.Count -eq 0) {
        throw "No se pudo comprobar la publicacion de puertos de PostgreSQL."
    }

    $portBindings = ([string]($portBindingLines | Select-Object -Last 1)).Trim()
    if ($portBindings -ne "{}" -and $portBindings -ne "null") {
        throw "PostgreSQL productivo tiene puertos publicados; se aborto la prueba."
    }

    return [PSCustomObject][ordered]@{
        status = "healthy"
        services = @($serviceStatuses)
        postgres_5432_published = $false
    }
}

function Get-ProductionPostgresImage {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ComposeFile,

        [Parameter(Mandatory = $true)]
        [string]$EnvFile
    )

    $imageLines = @(
        & docker compose -f $ComposeFile --env-file $EnvFile `
            config --images 2>$null
    )
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo detectar la imagen PostgreSQL del Compose productivo."
    }

    $postgresImages = @(
        $imageLines |
            ForEach-Object { ([string]$_).Trim() } |
            Where-Object { $_ -match "(^|/)postgres([:@]|$)" }
    )
    if ($postgresImages.Count -ne 1) {
        throw "No se pudo identificar una unica imagen PostgreSQL productiva."
    }

    return $postgresImages[0]
}

function New-TemporaryPassword {
    $bytes = New-Object byte[] 36
    $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $generator.GetBytes($bytes)
    }
    finally {
        $generator.Dispose()
    }

    return ([Convert]::ToBase64String($bytes)).
        Replace("+", "A").
        Replace("/", "B").
        TrimEnd("=")
}

function Test-DockerContainerExists {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ContainerName
    )

    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "SilentlyContinue"
        & docker container inspect $ContainerName *> $null
        $inspectExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    return ($inspectExitCode -eq 0)
}

function Assert-TemporaryContainerIsolation {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ContainerName
    )

    $portBindingLines = @(
        & docker inspect --format '{{json .HostConfig.PortBindings}}' `
            $ContainerName 2>$null
    )
    if ($LASTEXITCODE -ne 0 -or $portBindingLines.Count -eq 0) {
        throw "No se pudo inspeccionar los puertos del contenedor temporal."
    }

    $portBindings = ([string]($portBindingLines | Select-Object -Last 1)).Trim()
    if ($portBindings -ne "{}" -and $portBindings -ne "null") {
        throw "El contenedor temporal tiene puertos publicados; se aborto la prueba."
    }

    $networkModeLines = @(
        & docker inspect --format '{{.HostConfig.NetworkMode}}' `
            $ContainerName 2>$null
    )
    if ($LASTEXITCODE -ne 0 -or $networkModeLines.Count -eq 0) {
        throw "No se pudo inspeccionar la red del contenedor temporal."
    }

    $networkMode = ([string]($networkModeLines | Select-Object -Last 1)).Trim()
    if ($networkMode -ne "none") {
        throw "El contenedor temporal no quedo con red aislada."
    }

    $mountLines = @(
        & docker inspect --format `
            '{{range .Mounts}}{{println .Type "|" .Destination}}{{end}}' `
            $ContainerName 2>$null
    )
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo inspeccionar los mounts del contenedor temporal."
    }

    $volumeMounts = @(
        $mountLines | Where-Object {
            ([string]$_).Trim().StartsWith("volume |")
        }
    )
    if ($volumeMounts.Count -gt 0) {
        throw "El contenedor temporal creo o monto un volumen Docker; se aborto la prueba."
    }
}

function Wait-TemporaryPostgres {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ContainerName
    )

    for ($attempt = 1; $attempt -le 60; $attempt++) {
        $previousErrorActionPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = "SilentlyContinue"
            & docker exec $ContainerName `
                pg_isready -U restore_user -d restore_db *> $null
            $readyExitCode = $LASTEXITCODE
        }
        finally {
            $ErrorActionPreference = $previousErrorActionPreference
        }

        if ($readyExitCode -eq 0) {
            return
        }

        Start-Sleep -Seconds 1
    }

    throw "PostgreSQL temporal no estuvo listo dentro del tiempo esperado."
}

function Invoke-RestorePsqlScalar {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ContainerName,

        [Parameter(Mandatory = $true)]
        [string]$Sql
    )

    $resultLines = @(
        & docker exec $ContainerName `
            psql -X -U restore_user -d restore_db -At `
                -v ON_ERROR_STOP=1 -c $Sql 2>$null
    )
    if ($LASTEXITCODE -ne 0) {
        throw "Una validacion SQL de la restauracion fallo."
    }

    $values = @(
        $resultLines |
            ForEach-Object { ([string]$_).Trim() } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    )
    if ($values.Count -ne 1) {
        throw "Una validacion SQL devolvio un resultado inesperado."
    }

    return $values[0]
}

function Assert-EvidencePathIgnored {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,

        [Parameter(Mandatory = $true)]
        [string]$RelativeDirectory
    )

    if ($null -eq (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git no esta disponible para comprobar que la evidencia este ignorada."
    }

    $probePath = "$RelativeDirectory/restore-test-ignore-probe.json"
    & git -C $RepoRoot check-ignore --quiet -- $probePath
    if ($LASTEXITCODE -ne 0) {
        throw "La ruta $RelativeDirectory no esta ignorada por Git."
    }
}

$createdAt = (Get-Date).ToUniversalTime().ToString("o")
$containerName = ""
$containerCreated = $false
$evidencePath = ""
$selectedBackup = $null
$backupSize = 0
$backupHash = "unavailable"
$postgresImage = "unavailable"
$alembicVersionRestored = "not_checked"
$tableValidationStatus = "NOT_RUN"
$rowCounts = [ordered]@{}
$pgRestoreListStatus = "NOT_RUN"
$restoreStatus = "NOT_RUN"
$productionHealthBefore = $null
$productionHealthAfter = $null
$cleanupStatus = "NOT_NEEDED"
$failureMessage = ""

Push-Location $RepoRoot
try {
    Assert-ProdLocalPrerequisites `
        -RepoRoot $RepoRoot `
        -ComposeFile $ComposeFile `
        -EnvFile $EnvFile
    Test-ProdComposeConfiguration -ComposeFile $ComposeFile -EnvFile $EnvFile
    Assert-EvidencePathIgnored `
        -RepoRoot $RepoRoot `
        -RelativeDirectory $EvidenceRelativeDirectory

    $productionHealthBefore = Get-SafeProductionHealth `
        -ComposeFile $ComposeFile `
        -EnvFile $EnvFile
    Write-Host "Produccion antes de la prueba: db/api/web healthy; PostgreSQL 5432 sin publicar." `
        -ForegroundColor Green

    if ([string]::IsNullOrWhiteSpace($BackupPath)) {
        if (-not (Test-Path -LiteralPath $BackupDirectory -PathType Container)) {
            throw "No existe la carpeta de backups: $BackupDirectory"
        }

        $selectedBackup = @(
            Get-ChildItem -LiteralPath $BackupDirectory -File -Filter "*.dump" |
                Sort-Object -Property LastWriteTimeUtc -Descending |
                Select-Object -First 1
        )
        if ($selectedBackup.Count -eq 0) {
            throw "No hay backups .dump en $BackupDirectory."
        }
        $selectedBackup = $selectedBackup[0]
    }
    else {
        $candidatePath = if ([IO.Path]::IsPathRooted($BackupPath)) {
            $BackupPath
        }
        else {
            Join-Path $RepoRoot $BackupPath
        }

        if (-not (Test-Path -LiteralPath $candidatePath -PathType Leaf)) {
            throw "No existe el backup indicado."
        }
        $selectedBackup = Get-Item -LiteralPath (Resolve-Path -LiteralPath $candidatePath).Path
    }

    if ($selectedBackup.Extension -ne ".dump") {
        throw "El archivo de backup debe tener extension .dump."
    }
    if ($selectedBackup.Length -le 0) {
        throw "El archivo de backup esta vacio."
    }

    $backupSize = [Int64]$selectedBackup.Length
    $backupHash = (Get-FileHash `
        -LiteralPath $selectedBackup.FullName `
        -Algorithm SHA256).Hash.ToLowerInvariant()
    $sha256Path = "$($selectedBackup.FullName).sha256"
    if (Test-Path -LiteralPath $sha256Path -PathType Leaf) {
        $sha256Text = Get-Content -Raw -LiteralPath $sha256Path
        $sha256Match = [Regex]::Match(
            $sha256Text,
            "(?im)^\s*([0-9a-f]{64})(?:\s+.*)?\s*$"
        )
        if (-not $sha256Match.Success) {
            throw "El archivo SHA256 no tiene un formato valido."
        }

        $expectedHash = $sha256Match.Groups[1].Value.ToLowerInvariant()
        if ($backupHash -ne $expectedHash) {
            throw "El SHA256 del backup no coincide; se aborto antes de restaurar."
        }
        Write-Host "SHA256: OK ($backupHash)" -ForegroundColor Green
    }
    else {
        Write-Warning "El backup no tiene archivo .sha256; se calculo el hash, pero no fue posible compararlo."
    }

    if (-not (Test-Path -LiteralPath $EvidenceDirectory -PathType Container)) {
        New-Item -ItemType Directory -Path $EvidenceDirectory -Force | Out-Null
    }

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $suffix = 0
    do {
        $suffixText = if ($suffix -eq 0) { "" } else { "-$suffix" }
        $containerName = "agua-activa-restore-test-$timestamp$suffixText"
        $evidencePath = Join-Path `
            $EvidenceDirectory `
            "restore-test-$timestamp$suffixText.json"
        $suffix++
    } while (
        (Test-DockerContainerExists -ContainerName $containerName) -or
        (Test-Path -LiteralPath $evidencePath)
    )

    $postgresImage = Get-ProductionPostgresImage `
        -ComposeFile $ComposeFile `
        -EnvFile $EnvFile
    Write-Host "Imagen PostgreSQL temporal: $postgresImage"
    Write-Host "Creando contenedor temporal aislado: $containerName"

    $temporaryPassword = New-TemporaryPassword
    $previousProcessPassword = [Environment]::GetEnvironmentVariable(
        "POSTGRES_PASSWORD",
        [EnvironmentVariableTarget]::Process
    )
    $dockerRunExitCode = 1
    try {
        [Environment]::SetEnvironmentVariable(
            "POSTGRES_PASSWORD",
            $temporaryPassword,
            [EnvironmentVariableTarget]::Process
        )
        & docker run --detach `
            --name $containerName `
            --network none `
            --tmpfs "/var/lib/postgresql/data:rw,nosuid,size=1g" `
            --env "POSTGRES_USER=restore_user" `
            --env "POSTGRES_DB=restore_db" `
            --env POSTGRES_PASSWORD `
            $postgresImage *> $null
        $dockerRunExitCode = $LASTEXITCODE
    }
    finally {
        [Environment]::SetEnvironmentVariable(
            "POSTGRES_PASSWORD",
            $previousProcessPassword,
            [EnvironmentVariableTarget]::Process
        )
        $temporaryPassword = $null
    }

    if ($dockerRunExitCode -ne 0) {
        throw "Docker no pudo crear el contenedor PostgreSQL temporal."
    }
    $containerCreated = $true

    Assert-TemporaryContainerIsolation -ContainerName $containerName
    Write-Host "Aislamiento: OK (sin red, sin puertos publicados y sin volumen Docker)." `
        -ForegroundColor Green

    Wait-TemporaryPostgres -ContainerName $containerName
    Write-Host "PostgreSQL temporal: listo." -ForegroundColor Green

    & docker cp `
        $selectedBackup.FullName `
        "${containerName}:/tmp/backup.dump" *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo copiar el dump al contenedor temporal."
    }

    & docker exec $containerName `
        pg_restore --list /tmp/backup.dump *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "pg_restore --list no pudo validar el dump en el contenedor temporal."
    }
    $pgRestoreListStatus = "OK"
    Write-Host "pg_restore --list: OK" -ForegroundColor Green

    & docker exec $containerName `
        pg_restore `
            --no-owner `
            --no-privileges `
            --exit-on-error `
            -U restore_user `
            -d restore_db `
            /tmp/backup.dump *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "pg_restore fallo al restaurar en el contenedor temporal."
    }
    $restoreStatus = "OK"
    Write-Host "Restauracion real en el contenedor temporal: OK" `
        -ForegroundColor Green

    $alembicTableExists = Invoke-RestorePsqlScalar `
        -ContainerName $containerName `
        -Sql "SELECT to_regclass('public.alembic_version') IS NOT NULL;"
    if ($alembicTableExists -ne "t") {
        throw "La restauracion no contiene la tabla alembic_version."
    }

    $alembicVersionRestored = Invoke-RestorePsqlScalar `
        -ContainerName $containerName `
        -Sql "SELECT version_num FROM public.alembic_version;"
    if ($alembicVersionRestored -ne $ExpectedAlembicVersion) {
        throw "Alembic restaurado no coincide con la revision esperada."
    }
    Write-Host "Alembic restaurado: $alembicVersionRestored" `
        -ForegroundColor Green

    foreach ($table in $ExpectedTables) {
        $tableExists = Invoke-RestorePsqlScalar `
            -ContainerName $containerName `
            -Sql "SELECT to_regclass('public.$table') IS NOT NULL;"
        if ($tableExists -ne "t") {
            throw "Falta una tabla principal esperada: $table"
        }

        $countValue = Invoke-RestorePsqlScalar `
            -ContainerName $containerName `
            -Sql "SELECT COUNT(*) FROM public.$table;"
        $parsedCount = 0L
        if (-not [Int64]::TryParse($countValue, [ref]$parsedCount)) {
            throw "Un conteo restaurado no es numerico."
        }
        $rowCounts[$table] = $parsedCount
    }
    $tableValidationStatus = "OK"
    Write-Host "Tablas principales y conteos numericos: OK" `
        -ForegroundColor Green

    $productionHealthAfter = Get-SafeProductionHealth `
        -ComposeFile $ComposeFile `
        -EnvFile $EnvFile
    Write-Host "Produccion despues del restore: db/api/web healthy; PostgreSQL 5432 sin publicar." `
        -ForegroundColor Green
}
catch {
    $failureMessage = $_.Exception.Message
    if ($restoreStatus -eq "NOT_RUN") {
        $restoreStatus = "FAILED"
    }
    if ($tableValidationStatus -eq "NOT_RUN" -and
        $alembicVersionRestored -ne "not_checked") {
        $tableValidationStatus = "FAILED"
    }
}
finally {
    if ($null -ne $productionHealthBefore -and
        $null -eq $productionHealthAfter) {
        try {
            $productionHealthAfter = Get-SafeProductionHealth `
                -ComposeFile $ComposeFile `
                -EnvFile $EnvFile
        }
        catch {
            $productionHealthAfter = [PSCustomObject][ordered]@{
                status = "unavailable"
            }
            if ([string]::IsNullOrWhiteSpace($failureMessage)) {
                $failureMessage = "No se pudo validar la salud productiva despues de la prueba."
            }
            else {
                Write-Warning "No se pudo validar la salud productiva despues del fallo."
            }
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($containerName) -and
        (Test-DockerContainerExists -ContainerName $containerName)) {
        if (-not [string]::IsNullOrWhiteSpace($failureMessage) -and
            $KeepContainer) {
            $cleanupStatus = "KEPT_FOR_DEBUGGING"
            Write-Warning "El contenedor temporal se conservo por -KeepContainer: $containerName"
        }
        else {
            $previousErrorActionPreference = $ErrorActionPreference
            try {
                $ErrorActionPreference = "SilentlyContinue"
                & docker rm --force --volumes $containerName *> $null
                $removeExitCode = $LASTEXITCODE
            }
            finally {
                $ErrorActionPreference = $previousErrorActionPreference
            }

            if ($removeExitCode -eq 0 -and
                -not (Test-DockerContainerExists -ContainerName $containerName)) {
                $cleanupStatus = "OK"
                $containerCreated = $false
            }
            else {
                $cleanupStatus = "FAILED"
                if ([string]::IsNullOrWhiteSpace($failureMessage)) {
                    $failureMessage = "No se pudo eliminar el contenedor temporal."
                }
            }
        }
    }
    elseif ($containerCreated) {
        $cleanupStatus = "FAILED"
        if ([string]::IsNullOrWhiteSpace($failureMessage)) {
            $failureMessage = "No se pudo confirmar la limpieza del contenedor temporal."
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($evidencePath)) {
        $safeBackupName = if ($null -eq $selectedBackup) {
            "unavailable"
        }
        else {
            $selectedBackup.Name
        }

        $evidence = [ordered]@{
            created_at = $createdAt
            pc_name = [Environment]::MachineName
            backup_file = $safeBackupName
            backup_size_bytes = $backupSize
            backup_sha256 = $backupHash
            restore_container_name = $containerName
            postgres_image = $postgresImage
            alembic_version_restored = $alembicVersionRestored
            expected_alembic_version = $ExpectedAlembicVersion
            table_validation_status = $tableValidationStatus
            row_counts_by_table = $rowCounts
            pg_restore_list_status = $pgRestoreListStatus
            restore_status = $restoreStatus
            production_health_before = $productionHealthBefore
            production_health_after = $productionHealthAfter
            cleanup_status = $cleanupStatus
            note = "No contiene secretos ni datos de negocio en texto plano."
        }
        $evidence |
            ConvertTo-Json -Depth 8 |
            Set-Content -LiteralPath $evidencePath -Encoding UTF8
    }

    Pop-Location
}

if (-not [string]::IsNullOrWhiteSpace($failureMessage)) {
    Write-Host ""
    Write-Host "ERROR: La prueba de restauracion controlada fallo: $failureMessage" `
        -ForegroundColor Red
    if (-not [string]::IsNullOrWhiteSpace($evidencePath)) {
        Write-Host "Evidencia segura: $evidencePath"
    }
    exit 1
}

Write-Host ""
Write-Host "RESULTADO: OK. Backup restaurado y validado sin tocar produccion." `
    -ForegroundColor Green
Write-Host "Evidencia segura: $evidencePath"
Write-Host "Cleanup del contenedor temporal: $cleanupStatus"
Write-Host "Comprobacion recomendada:"
Write-Host "powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-health.ps1"

exit 0
