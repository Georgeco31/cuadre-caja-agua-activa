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

    Write-Host "Iniciando Agua Activa ERP sin reconstruir imagenes..."
    Invoke-ProdCompose -ComposeFile $ComposeFile -EnvFile $EnvFile -CommandArguments @("up", "-d")

    Write-Host ""
    Write-Host "Agua Activa ERP iniciado." -ForegroundColor Green
    Write-Host "LAN: $LanWebUrl"
    Write-Host "Tailscale: $TailscaleWebUrl"
    Write-Host "API LAN: $LanApiHealthUrl"
    Write-Host "API Tailscale: $TailscaleApiHealthUrl"
    Write-Host ""
    Write-Host "Siguiente paso sugerido:"
    Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-health.ps1"
}
catch {
    Write-ProdError "No se pudo iniciar Agua Activa ERP. $($_.Exception.Message)"
    $exitCode = 1
}
finally {
    Pop-Location
}

exit $exitCode
