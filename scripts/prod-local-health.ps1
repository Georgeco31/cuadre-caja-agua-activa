Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ComposeFile = "docker-compose.prod.yml"
$EnvFile = ".env.production.local"
$LanWebUrl = "http://192.168.100.220:3000/login"
$LanApiHealthUrl = "http://192.168.100.220:8010/api/v1/health"
$TailscaleWebUrl = "http://100.121.163.126:3000/login"
$TailscaleApiHealthUrl = "http://100.121.163.126:8010/api/v1/health"
$LocalWebUrl = "http://localhost:3000/login"
$LocalApiHealthUrl = "http://localhost:8010/api/v1/health"

. (Join-Path $PSScriptRoot "prod-local-common.ps1")

$script:CriticalFailures = 0
$script:Warnings = 0

function Write-HealthResult {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("OK", "FAIL", "WARNING")]
        [string]$Level,

        [Parameter(Mandatory = $true)]
        [string]$Section,

        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    $color = switch ($Level) {
        "OK" { "Green" }
        "FAIL" { "Red" }
        "WARNING" { "Yellow" }
    }

    Write-Host "$Level [$Section] $Message" -ForegroundColor $color
    if ($Level -eq "FAIL") {
        $script:CriticalFailures++
    }
    elseif ($Level -eq "WARNING") {
        $script:Warnings++
    }
}

function Test-ApiEndpoint {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Section,

        [Parameter(Mandatory = $true)]
        [string]$Url,

        [switch]$Informational
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        $body = $response.Content | ConvertFrom-Json
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300 -and
            $null -ne $body.status -and $body.status -eq "ok") {
            Write-HealthResult -Level "OK" -Section $Section -Message "API responde con status=ok en $Url"
        }
        else {
            $level = if ($Informational) { "WARNING" } else { "FAIL" }
            Write-HealthResult -Level $level -Section $Section -Message "La API respondio, pero no con status=ok en $Url"
        }
    }
    catch {
        $level = if ($Informational) { "WARNING" } else { "FAIL" }
        Write-HealthResult -Level $level -Section $Section -Message "No fue posible conectar con $Url"
    }
}

function Test-WebEndpoint {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Section,

        [Parameter(Mandatory = $true)]
        [string]$Url,

        [switch]$Informational
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
            Write-HealthResult -Level "OK" -Section $Section -Message "Web responde en $Url"
        }
        else {
            $level = if ($Informational) { "WARNING" } else { "FAIL" }
            Write-HealthResult -Level $level -Section $Section -Message "Web devolvio HTTP $($response.StatusCode) en $Url"
        }
    }
    catch {
        $level = if ($Informational) { "WARNING" } else { "FAIL" }
        Write-HealthResult -Level $level -Section $Section -Message "No fue posible conectar con $Url"
    }
}

function ConvertFrom-ComposePsJson {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Lines
    )

    $nonEmptyLines = @($Lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
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

function Get-JsonPropertyValue {
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

$exitCode = 0
Push-Location $RepoRoot
try {
    try {
        Assert-ProdLocalPrerequisites -RepoRoot $RepoRoot -ComposeFile $ComposeFile -EnvFile $EnvFile
        Assert-ProdEnvironmentValues -RepoRoot $RepoRoot -EnvFile $EnvFile
        Write-HealthResult -Level "OK" -Section "Requisitos" -Message "Archivos, Docker y variables requeridas disponibles."
    }
    catch {
        Write-HealthResult -Level "FAIL" -Section "Requisitos" -Message $_.Exception.Message
        throw
    }

    try {
        Test-ProdComposeConfiguration -ComposeFile $ComposeFile -EnvFile $EnvFile
        Write-HealthResult -Level "OK" -Section "Compose" -Message "docker compose config --quiet aprobo."
    }
    catch {
        Write-HealthResult -Level "FAIL" -Section "Compose" -Message $_.Exception.Message
    }

    Write-Host ""
    Write-Host "Estado reportado por Docker Compose:"
    & docker compose -f $ComposeFile --env-file $EnvFile ps
    if ($LASTEXITCODE -ne 0) {
        Write-HealthResult -Level "FAIL" -Section "Contenedores" -Message "docker compose ps fallo."
    }

    $psLines = @(& docker compose -f $ComposeFile --env-file $EnvFile ps --format json 2>$null)
    if ($LASTEXITCODE -ne 0) {
        Write-HealthResult -Level "FAIL" -Section "Contenedores" -Message "No se pudo obtener el estado estructurado."
        $containers = @()
    }
    else {
        try {
            $containers = @(ConvertFrom-ComposePsJson -Lines $psLines)
        }
        catch {
            Write-HealthResult -Level "FAIL" -Section "Contenedores" -Message "No se pudo interpretar el estado de Docker Compose."
            $containers = @()
        }
    }

    foreach ($service in @("db", "api", "web")) {
        $container = @($containers | Where-Object {
            (Get-JsonPropertyValue -InputObject $_ -PropertyName "Service") -eq $service
        } | Select-Object -First 1)
        if ($container.Count -eq 0) {
            Write-HealthResult -Level "FAIL" -Section "Contenedores" -Message "El servicio $service no esta creado."
            continue
        }

        $state = [string](Get-JsonPropertyValue -InputObject $container[0] -PropertyName "State")
        $health = [string](Get-JsonPropertyValue -InputObject $container[0] -PropertyName "Health")
        if ($state -ne "running") {
            Write-HealthResult -Level "FAIL" -Section "Contenedores" -Message "El servicio $service esta en estado $state."
        }
        elseif (-not [string]::IsNullOrWhiteSpace($health) -and $health -ne "healthy") {
            Write-HealthResult -Level "FAIL" -Section "Contenedores" -Message "El servicio $service esta activo, health=$health."
        }
        else {
            $healthText = if ([string]::IsNullOrWhiteSpace($health)) { "sin health reportado" } else { "health=$health" }
            Write-HealthResult -Level "OK" -Section "Contenedores" -Message "$service activo, $healthText."
        }
    }

    Test-ApiEndpoint -Section "API localhost" -Url $LocalApiHealthUrl
    Test-ApiEndpoint -Section "API LAN" -Url $LanApiHealthUrl
    Test-ApiEndpoint -Section "API Tailscale" -Url $TailscaleApiHealthUrl -Informational
    Test-WebEndpoint -Section "Web LAN" -Url $LanWebUrl
    Test-WebEndpoint -Section "Web Tailscale" -Url $TailscaleWebUrl -Informational

    try {
        $currentVersion = Get-ProdAlembicVersion -ComposeFile $ComposeFile -EnvFile $EnvFile
        if ($currentVersion -eq "0028_payroll_base") {
            Write-HealthResult -Level "OK" -Section "Alembic" -Message "La revision actual es 0028_payroll_base."
        }
        else {
            Write-HealthResult -Level "FAIL" -Section "Alembic" -Message "La revision actual no es 0028_payroll_base; se obtuvo $currentVersion."
        }
    }
    catch {
        Write-HealthResult -Level "FAIL" -Section "Alembic" -Message $_.Exception.Message
    }

    $configJsonLines = @(& docker compose -f $ComposeFile --env-file $EnvFile config --format json 2>$null)
    if ($LASTEXITCODE -ne 0) {
        Write-HealthResult -Level "FAIL" -Section "PostgreSQL" -Message "No se pudo inspeccionar la configuracion resuelta."
    }
    else {
        try {
            $configObject = ($configJsonLines -join [Environment]::NewLine) | ConvertFrom-Json
            $servicesObject = Get-JsonPropertyValue -InputObject $configObject -PropertyName "services"
            $dbConfig = Get-JsonPropertyValue -InputObject $servicesObject -PropertyName "db"
            $configuredDbPortsValue = Get-JsonPropertyValue -InputObject $dbConfig -PropertyName "ports"
            $configuredDbPorts = @()
            if ($null -ne $configuredDbPortsValue) {
                $configuredDbPorts = @($configuredDbPortsValue)
            }
            $dbContainers = @($containers | Where-Object {
                (Get-JsonPropertyValue -InputObject $_ -PropertyName "Service") -eq "db"
            })
            $publishedDbPorts = @()
            foreach ($dbContainer in $dbContainers) {
                $publishersValue = Get-JsonPropertyValue -InputObject $dbContainer -PropertyName "Publishers"
                $publishers = @()
                if ($null -ne $publishersValue) {
                    $publishers = @($publishersValue)
                }
                $publishedDbPorts += @($publishers | Where-Object {
                    $null -ne $_ -and
                    [int](Get-JsonPropertyValue -InputObject $_ -PropertyName "PublishedPort") -gt 0
                })
            }

            if ($configuredDbPorts.Count -eq 0 -and $publishedDbPorts.Count -eq 0) {
                Write-HealthResult -Level "OK" -Section "PostgreSQL" -Message "El puerto 5432 no esta publicado por Compose."
            }
            else {
                Write-HealthResult -Level "FAIL" -Section "PostgreSQL" -Message "El servicio db tiene un puerto publicado; revise Compose sin mostrar secretos."
            }
        }
        catch {
            Write-HealthResult -Level "FAIL" -Section "PostgreSQL" -Message "No se pudo interpretar la configuracion de puertos."
        }
    }

    if ($null -eq (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-HealthResult -Level "WARNING" -Section "Git" -Message "Git no esta disponible; no se pudo comprobar $EnvFile."
    }
    else {
        & git rev-parse --is-inside-work-tree *> $null
        if ($LASTEXITCODE -ne 0) {
            Write-HealthResult -Level "WARNING" -Section "Git" -Message "La carpeta no parece un repositorio Git."
        }
        else {
            $trackedEnvPaths = @(& git ls-files -- $EnvFile 2>$null)
            if ($LASTEXITCODE -ne 0) {
                Write-HealthResult -Level "WARNING" -Section "Git" -Message "No se pudo consultar el estado de $EnvFile."
            }
            elseif ($trackedEnvPaths.Count -gt 0) {
                Write-HealthResult -Level "FAIL" -Section "Git" -Message "$EnvFile esta versionado y debe retirarse de Git sin borrar el archivo local."
            }
            else {
                & git check-ignore -q -- $EnvFile
                if ($LASTEXITCODE -eq 0) {
                    Write-HealthResult -Level "OK" -Section "Git" -Message "$EnvFile no esta versionado y esta ignorado."
                }
                else {
                    Write-HealthResult -Level "WARNING" -Section "Git" -Message "$EnvFile no esta versionado, pero no figura ignorado."
                }
            }
        }
    }
}
catch {
    if ($script:CriticalFailures -eq 0) {
        Write-HealthResult -Level "FAIL" -Section "General" -Message $_.Exception.Message
    }
}
finally {
    Pop-Location
}

Write-Host ""
if ($script:CriticalFailures -eq 0) {
    Write-Host "RESULTADO: OK. Fallos criticos: 0. Advertencias informativas: $script:Warnings." -ForegroundColor Green
}
else {
    Write-Host "RESULTADO: FAIL. Fallos criticos: $script:CriticalFailures. Advertencias informativas: $script:Warnings." -ForegroundColor Red
    Write-Host "Revise: powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-logs.ps1"
    $exitCode = 1
}

exit $exitCode
