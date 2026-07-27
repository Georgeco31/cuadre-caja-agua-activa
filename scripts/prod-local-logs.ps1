param(
    [ValidateSet("api", "web", "db", "all")]
    [string]$Service = "all",

    [ValidateRange(1, 100000)]
    [int]$Tail = 100
)

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

    $commandArguments = @("logs", "--tail", $Tail.ToString())
    if ($Service -ne "all") {
        $commandArguments += $Service
    }

    Write-Host "Logs recientes: servicio=$Service, lineas=$Tail"
    Invoke-ProdCompose -ComposeFile $ComposeFile -EnvFile $EnvFile -CommandArguments $commandArguments
}
catch {
    Write-ProdError "No se pudieron consultar los logs. $($_.Exception.Message)"
    $exitCode = 1
}
finally {
    Pop-Location
}

exit $exitCode
