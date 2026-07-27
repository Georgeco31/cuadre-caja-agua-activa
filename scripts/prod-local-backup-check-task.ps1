param(
    [ValidateNotNullOrEmpty()]
    [string]$TaskName = "AguaActivaERP-BackupDiario"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$TaskPath = "\"

foreach ($commandName in @("Get-ScheduledTask", "Get-ScheduledTaskInfo")) {
    if ($null -eq (Get-Command $commandName -ErrorAction SilentlyContinue)) {
        throw "El comando $commandName no esta disponible. Este script requiere Windows Task Scheduler."
    }
}

$task = Get-ScheduledTask `
    -TaskPath $TaskPath `
    -TaskName $TaskName `
    -ErrorAction SilentlyContinue
if ($null -eq $task) {
    Write-Host "Estado: no existe"
    Write-Host "Tarea: $TaskName"
    exit 0
}

$info = Get-ScheduledTaskInfo `
    -TaskPath $TaskPath `
    -TaskName $TaskName `
    -ErrorAction Stop

function Format-TaskDate {
    param(
        [Parameter(Mandatory = $true)]
        [DateTime]$Value
    )

    if ($Value -eq [DateTime]::MinValue -or $Value.Year -le 1900) {
        return "Sin ejecucion registrada"
    }

    return $Value.ToString("yyyy-MM-dd HH:mm:ss")
}

Write-Host "Estado: existe"
Write-Host "Tarea: $TaskName"
Write-Host "Estado actual: $($task.State)"
Write-Host "Proxima ejecucion: $(Format-TaskDate -Value $info.NextRunTime)"
Write-Host "Ultima ejecucion: $(Format-TaskDate -Value $info.LastRunTime)"
Write-Host "Ultimo resultado: $($info.LastTaskResult) (0 significa exito)"
