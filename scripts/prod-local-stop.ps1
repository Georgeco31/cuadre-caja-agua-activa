Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ComposeFile = "docker-compose.prod.yml"
$EnvFile = ".env.production.local"
$LanWebUrl = "http://192.168.100.225:3000/login"
$LanApiHealthUrl = "http://192.168.100.225:8010/api/v1/health"
$TailscaleWebUrl = "http://100.121.163.126:3000/login"
$TailscaleApiHealthUrl = "http://100.121.163.126:8010/api/v1/health"

. (Join-Path $PSScriptRoot "prod-local-common.ps1")

$exitCode = 0
Push-Location $RepoRoot
try {
    Assert-ProdLocalPrerequisites -RepoRoot $RepoRoot -ComposeFile $ComposeFile -EnvFile $EnvFile

    Write-Host "Apagando Agua Activa ERP de forma segura..."
    Invoke-ProdCompose -ComposeFile $ComposeFile -EnvFile $EnvFile -CommandArguments @("down")

    Write-Host ""
    Write-Host "Agua Activa ERP apagado." -ForegroundColor Green
    Write-Host "Los datos se conservan porque no se usa la opcion -v para eliminar volumenes." -ForegroundColor Yellow
    Write-Host "No se borraron volumenes, imagenes, backups ni $EnvFile."
}
catch {
    Write-ProdError "No se pudo apagar Agua Activa ERP. $($_.Exception.Message)"
    $exitCode = 1
}
finally {
    Pop-Location
}

exit $exitCode
