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
    Test-ProdComposeConfiguration -ComposeFile $ComposeFile -EnvFile $EnvFile

    Write-Host "Estado de los contenedores principales (db, api, web):"
    Invoke-ProdCompose -ComposeFile $ComposeFile -EnvFile $EnvFile -CommandArguments @("ps")

    Write-Host ""
    Write-Host "URLs:"
    Write-Host "  LAN: $LanWebUrl"
    Write-Host "  Tailscale: $TailscaleWebUrl"
    Write-Host "  API LAN: $LanApiHealthUrl"
    Write-Host "  API Tailscale: $TailscaleApiHealthUrl"
}
catch {
    Write-ProdError "No se pudo consultar el estado. $($_.Exception.Message)"
    $exitCode = 1
}
finally {
    Pop-Location
}

exit $exitCode
