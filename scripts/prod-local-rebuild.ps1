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

    Write-Host "ADVERTENCIA: confirme un backup reciente y comprobado antes de actualizar." -ForegroundColor Yellow
    Write-Host "Reconstruyendo Agua Activa ERP sin borrar volumenes..."
    Invoke-ProdCompose -ComposeFile $ComposeFile -EnvFile $EnvFile -CommandArguments @("up", "-d", "--build")

    Write-Host ""
    Write-Host "Reconstruccion terminada sin eliminar volumenes." -ForegroundColor Green
    Write-Host "Ejecute ahora:"
    Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-health.ps1"
}
catch {
    Write-ProdError "No se pudo reconstruir Agua Activa ERP. $($_.Exception.Message)"
    $exitCode = 1
}
finally {
    Pop-Location
}

exit $exitCode
