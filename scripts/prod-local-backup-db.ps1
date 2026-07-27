Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ComposeFile = "docker-compose.prod.yml"
$EnvFile = ".env.production.local"
$BackupRelativeDirectory = "backups/postgres"
$BackupDirectory = Join-Path $RepoRoot $BackupRelativeDirectory

. (Join-Path $PSScriptRoot "prod-local-common.ps1")

function ConvertFrom-BackupComposePsJson {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Lines
    )

    $nonEmptyLines = @($Lines | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    })
    if ($nonEmptyLines.Count -eq 0) {
        return @()
    }

    $joined = $nonEmptyLines -join [Environment]::NewLine
    try {
        return @($joined | ConvertFrom-Json)
    }
    catch {
        $items = @()
        foreach ($line in $nonEmptyLines) {
            $items += $line | ConvertFrom-Json
        }
        return @($items)
    }
}

function Get-BackupJsonPropertyValue {
    param(
        [Parameter(Mandatory = $true)]
        [object]$InputObject,

        [Parameter(Mandatory = $true)]
        [string]$PropertyName
    )

    $property = $InputObject.PSObject.Properties[$PropertyName]
    if ($null -eq $property) {
        return $null
    }

    return $property.Value
}

function Get-SafeDockerServicesStatus {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ComposeFile,

        [Parameter(Mandatory = $true)]
        [string]$EnvFile
    )

    $statusLines = @(
        & docker compose -f $ComposeFile --env-file $EnvFile ps --format json 2>$null
    )
    if ($LASTEXITCODE -ne 0) {
        return @(
            [PSCustomObject]@{
                service = "unknown"
                state = "unavailable"
                health = "unavailable"
            }
        )
    }

    try {
        $containers = @(ConvertFrom-BackupComposePsJson -Lines $statusLines)
        $safeStatus = @()
        foreach ($container in $containers) {
            $service = [string](Get-BackupJsonPropertyValue `
                -InputObject $container -PropertyName "Service")
            $state = [string](Get-BackupJsonPropertyValue `
                -InputObject $container -PropertyName "State")
            $health = [string](Get-BackupJsonPropertyValue `
                -InputObject $container -PropertyName "Health")
            if ([string]::IsNullOrWhiteSpace($health)) {
                $health = "not_reported"
            }

            $safeStatus += [PSCustomObject]@{
                service = $service
                state = $state
                health = $health
            }
        }
        return @($safeStatus)
    }
    catch {
        return @(
            [PSCustomObject]@{
                service = "unknown"
                state = "unavailable"
                health = "unavailable"
            }
        )
    }
}

function Get-SafeGitCommit {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    if ($null -eq (Get-Command git -ErrorAction SilentlyContinue)) {
        return "unavailable"
    }

    $commitLines = @(& git -C $RepoRoot rev-parse --verify HEAD 2>$null)
    if ($LASTEXITCODE -ne 0 -or $commitLines.Count -eq 0) {
        return "unavailable"
    }

    return ($commitLines | Select-Object -Last 1).Trim()
}

function Assert-BackupPathIgnored {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,

        [Parameter(Mandatory = $true)]
        [string]$RelativeBackupPath
    )

    if ($null -eq (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git no esta disponible; no se puede comprobar que backups/ este ignorado."
    }

    & git -C $RepoRoot check-ignore --quiet -- $RelativeBackupPath
    if ($LASTEXITCODE -ne 0) {
        throw "La ruta $RelativeBackupPath no esta ignorada por Git. Corrija .gitignore antes de crear el backup."
    }
}

$containerTempPath = ""
$containerTempCreated = $false

Push-Location $RepoRoot
try {
    Assert-ProdLocalPrerequisites `
        -RepoRoot $RepoRoot `
        -ComposeFile $ComposeFile `
        -EnvFile $EnvFile
    Test-ProdComposeConfiguration -ComposeFile $ComposeFile -EnvFile $EnvFile

    $runningServices = @(
        & docker compose -f $ComposeFile --env-file $EnvFile `
            ps --status running --services db 2>$null
    )
    if ($LASTEXITCODE -ne 0 -or
        -not ($runningServices | Where-Object { $_.Trim() -eq "db" })) {
        throw "El contenedor db no esta corriendo. Inicie y verifique el ERP antes del backup."
    }

    if (-not (Test-Path -LiteralPath $BackupDirectory -PathType Container)) {
        New-Item -ItemType Directory -Path $BackupDirectory -Force | Out-Null
    }

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $suffix = 0
    do {
        $suffixText = if ($suffix -eq 0) { "" } else { "-$suffix" }
        $backupFileName = "agua-activa-postgres-$timestamp$suffixText.dump"
        $dumpPath = Join-Path $BackupDirectory $backupFileName
        $sha256Path = "$dumpPath.sha256"
        $metadataPath = "$dumpPath.json"
        $suffix++
    } while (
        (Test-Path -LiteralPath $dumpPath) -or
        (Test-Path -LiteralPath $sha256Path) -or
        (Test-Path -LiteralPath $metadataPath)
    )

    $relativeDumpPath = "$BackupRelativeDirectory/$backupFileName"
    Assert-BackupPathIgnored `
        -RepoRoot $RepoRoot `
        -RelativeBackupPath $relativeDumpPath

    $containerTempPath = "/tmp/$backupFileName"
    Write-Host "Creando backup PostgreSQL en un temporal seguro del contenedor db..."
    $containerTempCreated = $true
    & docker compose -f $ComposeFile --env-file $EnvFile exec -T db `
        sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f "$1"' `
        backup-script $containerTempPath
    if ($LASTEXITCODE -ne 0) {
        throw "pg_dump termino con codigo $LASTEXITCODE."
    }

    Write-Host "Copiando el backup al host sin streaming binario de PowerShell..."
    & docker compose -f $ComposeFile --env-file $EnvFile `
        cp "db:$containerTempPath" $dumpPath
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose cp termino con codigo $LASTEXITCODE."
    }

    $dumpFile = Get-Item -LiteralPath $dumpPath
    if ($dumpFile.Length -le 0) {
        throw "El archivo copiado esta vacio."
    }

    Write-Host "Validando el formato con pg_restore --list..."
    & docker compose -f $ComposeFile --env-file $EnvFile exec -T db `
        pg_restore --list $containerTempPath *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "pg_restore --list no pudo validar el backup."
    }
    $validationStatus = "OK: pg_restore --list"

    $hash = (Get-FileHash -LiteralPath $dumpPath -Algorithm SHA256).Hash.ToLowerInvariant()
    Set-Content `
        -LiteralPath $sha256Path `
        -Value "$hash  $backupFileName" `
        -Encoding Ascii

    try {
        $alembicVersion = Get-ProdAlembicVersion `
            -ComposeFile $ComposeFile `
            -EnvFile $EnvFile
    }
    catch {
        $alembicVersion = "unavailable"
        Write-Warning "No fue posible incluir la revision de Alembic en la metadata."
    }

    $metadata = [ordered]@{
        created_at = (Get-Date).ToUniversalTime().ToString("o")
        pc_name = [Environment]::MachineName
        repo_path = $RepoRoot
        backup_file = $backupFileName
        size_bytes = $dumpFile.Length
        sha256 = $hash
        alembic_version = $alembicVersion
        git_commit = Get-SafeGitCommit -RepoRoot $RepoRoot
        docker_services_status = @(
            Get-SafeDockerServicesStatus `
                -ComposeFile $ComposeFile `
                -EnvFile $EnvFile
        )
        validation_status = $validationStatus
        note = "No contiene secretos."
    }
    $metadata |
        ConvertTo-Json -Depth 5 |
        Set-Content -LiteralPath $metadataPath -Encoding UTF8

    Write-Host ""
    Write-Host "Backup creado: $dumpPath" -ForegroundColor Green
    Write-Host "Tamano: $($dumpFile.Length) bytes"
    Write-Host "SHA256: $hash"
    Write-Host "Validacion: $validationStatus" -ForegroundColor Green
    Write-Host "Metadata segura: $metadataPath"
    Write-Host ""
    Write-Host "Este backup todavia debe probarse con restauracion en el Bloque 56B." `
        -ForegroundColor Yellow
}
finally {
    if ($containerTempCreated -and
        -not [string]::IsNullOrWhiteSpace($containerTempPath)) {
        & docker compose -f $ComposeFile --env-file $EnvFile exec -T db `
            sh -c 'rm -f -- "$1"' backup-script $containerTempPath *> $null
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "No se pudo eliminar el archivo temporal del contenedor: $containerTempPath"
        }
    }
    Pop-Location
}
