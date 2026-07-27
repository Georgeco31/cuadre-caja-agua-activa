Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-ProdError {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host "ERROR: $Message" -ForegroundColor Red
}

function Assert-ProdLocalPrerequisites {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,

        [Parameter(Mandatory = $true)]
        [string]$ComposeFile,

        [Parameter(Mandatory = $true)]
        [string]$EnvFile
    )

    $composePath = Join-Path $RepoRoot $ComposeFile
    $envPath = Join-Path $RepoRoot $EnvFile

    if (-not (Test-Path -LiteralPath $composePath -PathType Leaf)) {
        throw "No existe el archivo requerido: $composePath"
    }

    if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
        throw "No existe el archivo requerido: $envPath"
    }

    if ($null -eq (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker no esta instalado o no esta disponible en PATH."
    }

    & docker compose version *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose v2 no esta disponible."
    }

    & docker info --format "{{.ServerVersion}}" *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Desktop no esta iniciado o el usuario no puede acceder al motor Docker."
    }
}

function Get-ProdEnvValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$EnvPath,

        [Parameter(Mandatory = $true)]
        [string]$Key
    )

    $escapedKey = [Regex]::Escape($Key)
    $matchingLine = Get-Content -LiteralPath $EnvPath |
        Where-Object { $_ -match "^\s*$escapedKey\s*=" } |
        Select-Object -Last 1

    if ($null -eq $matchingLine) {
        return ""
    }

    $value = ($matchingLine -replace "^\s*$escapedKey\s*=", "").Trim()
    if ($value.Length -ge 2) {
        $firstCharacter = $value.Substring(0, 1)
        $lastCharacter = $value.Substring($value.Length - 1, 1)
        if (($firstCharacter -eq '"' -and $lastCharacter -eq '"') -or
            ($firstCharacter -eq "'" -and $lastCharacter -eq "'")) {
            $value = $value.Substring(1, $value.Length - 2)
        }
    }

    return $value
}

function Assert-ProdEnvironmentValues {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,

        [Parameter(Mandatory = $true)]
        [string]$EnvFile
    )

    $envPath = Join-Path $RepoRoot $EnvFile
    $requiredKeys = @(
        "ENVIRONMENT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "DATABASE_URL",
        "AUTH_SECRET_KEY",
        "ADMIN_USERNAME",
        "ADMIN_PASSWORD",
        "CORS_ORIGINS",
        "NEXT_PUBLIC_API_URL"
    )

    foreach ($key in $requiredKeys) {
        $value = Get-ProdEnvValue -EnvPath $envPath -Key $key
        if ([string]::IsNullOrWhiteSpace($value)) {
            throw "La variable $key falta o esta vacia en $EnvFile."
        }
    }

    foreach ($key in @(
        "POSTGRES_PASSWORD",
        "DATABASE_URL",
        "AUTH_SECRET_KEY",
        "ADMIN_PASSWORD",
        "CORS_ORIGINS",
        "NEXT_PUBLIC_API_URL"
    )) {
        $value = Get-ProdEnvValue -EnvPath $envPath -Key $key
        if ($value -match "(?i)CHANGE_ME|SERVER_LAN_IP|REPLACE_ME") {
            throw "La variable $key todavia contiene un marcador de ejemplo."
        }
    }

    if ((Get-ProdEnvValue -EnvPath $envPath -Key "ENVIRONMENT") -ne "production") {
        throw "ENVIRONMENT debe ser production."
    }

    $databaseUrl = Get-ProdEnvValue -EnvPath $envPath -Key "DATABASE_URL"
    if (-not $databaseUrl.StartsWith("postgresql+psycopg://")) {
        throw "DATABASE_URL debe usar postgresql+psycopg://."
    }

    $corsOrigins = Get-ProdEnvValue -EnvPath $envPath -Key "CORS_ORIGINS"
    if ($corsOrigins.Contains("*")) {
        throw "CORS_ORIGINS no puede permitir el comodin *."
    }

    foreach ($key in @("API_PORT", "WEB_PORT")) {
        $value = Get-ProdEnvValue -EnvPath $envPath -Key $key
        if (-not [string]::IsNullOrWhiteSpace($value) -and $value -notmatch "^\d+$") {
            throw "La variable $key debe ser un puerto numerico."
        }
    }

    if ((Get-ProdEnvValue -EnvPath $envPath -Key "AUTH_SECRET_KEY").Length -lt 32) {
        throw "AUTH_SECRET_KEY debe tener al menos 32 caracteres."
    }

    if ((Get-ProdEnvValue -EnvPath $envPath -Key "POSTGRES_PASSWORD").Length -lt 16) {
        throw "POSTGRES_PASSWORD debe tener al menos 16 caracteres."
    }

    if ((Get-ProdEnvValue -EnvPath $envPath -Key "ADMIN_PASSWORD").Length -lt 12) {
        throw "ADMIN_PASSWORD debe tener al menos 12 caracteres."
    }
}

function Invoke-ProdCompose {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ComposeFile,

        [Parameter(Mandatory = $true)]
        [string]$EnvFile,

        [Parameter(Mandatory = $true)]
        [string[]]$CommandArguments
    )

    & docker compose -f $ComposeFile --env-file $EnvFile @CommandArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose termino con codigo $LASTEXITCODE."
    }
}

function Test-ProdComposeConfiguration {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ComposeFile,

        [Parameter(Mandatory = $true)]
        [string]$EnvFile
    )

    & docker compose -f $ComposeFile --env-file $EnvFile config --quiet
    if ($LASTEXITCODE -ne 0) {
        throw "La configuracion de Docker Compose no es valida."
    }
}

function Get-ProdAlembicVersion {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ComposeFile,

        [Parameter(Mandatory = $true)]
        [string]$EnvFile
    )

    $databaseUser = @(& docker compose -f $ComposeFile --env-file $EnvFile exec -T db printenv POSTGRES_USER 2>$null)
    if ($LASTEXITCODE -ne 0 -or $databaseUser.Count -eq 0) {
        throw "No se pudo leer POSTGRES_USER dentro del contenedor db."
    }

    $databaseName = @(& docker compose -f $ComposeFile --env-file $EnvFile exec -T db printenv POSTGRES_DB 2>$null)
    if ($LASTEXITCODE -ne 0 -or $databaseName.Count -eq 0) {
        throw "No se pudo leer POSTGRES_DB dentro del contenedor db."
    }

    $userValue = ($databaseUser | Select-Object -Last 1).Trim()
    $nameValue = ($databaseName | Select-Object -Last 1).Trim()
    $versionLines = @(
        & docker compose -f $ComposeFile --env-file $EnvFile exec -T db `
            psql -U $userValue -d $nameValue -Atc "SELECT version_num FROM alembic_version;" 2>$null
    )
    if ($LASTEXITCODE -ne 0 -or $versionLines.Count -eq 0) {
        throw "No se pudo consultar alembic_version mediante psql en db."
    }

    return ($versionLines | Select-Object -Last 1).Trim()
}
