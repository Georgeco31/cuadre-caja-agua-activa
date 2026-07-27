Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ComposeFile = "docker-compose.prod.yml"
$EnvFile = ".env.production.local"
$LanWebUrl = "http://192.168.100.220:3000/login"
$LanApiHealthUrl = "http://192.168.100.220:8010/api/v1/health"
$TailscaleWebUrl = "http://100.121.163.126:3000/login"
$TailscaleApiHealthUrl = "http://100.121.163.126:8010/api/v1/health"

. (Join-Path $PSScriptRoot "prod-local-common.ps1")

$exitCode = 0
Push-Location $RepoRoot
try {
    Assert-ProdLocalPrerequisites -RepoRoot $RepoRoot -ComposeFile $ComposeFile -EnvFile $EnvFile
    Assert-ProdEnvironmentValues -RepoRoot $RepoRoot -EnvFile $EnvFile
    Test-ProdComposeConfiguration -ComposeFile $ComposeFile -EnvFile $EnvFile

    Write-Host "ADVERTENCIA: ejecutar solo despues de backup y cuando haya actualizacion del sistema." -ForegroundColor Yellow
    Write-Host "Este script aplica migraciones; no ejecuta seeds."
    Invoke-ProdCompose -ComposeFile $ComposeFile -EnvFile $EnvFile -CommandArguments @(
        "run",
        "--rm",
        "api",
        "alembic",
        "upgrade",
        "head"
    )

    $alembicVersion = Get-ProdAlembicVersion -ComposeFile $ComposeFile -EnvFile $EnvFile
    Write-Host "Alembic actual: $alembicVersion" -ForegroundColor Green
}
catch {
    Write-ProdError "No se pudieron aplicar las migraciones. $($_.Exception.Message)"
    $exitCode = 1
}
finally {
    Pop-Location
}

exit $exitCode
