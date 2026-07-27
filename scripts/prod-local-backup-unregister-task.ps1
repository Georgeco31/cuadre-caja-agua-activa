[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Medium")]
param(
    [ValidateNotNullOrEmpty()]
    [string]$TaskName = "AguaActivaERP-BackupDiario",

    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$TaskPath = "\"

foreach ($commandName in @("Get-ScheduledTask", "Unregister-ScheduledTask")) {
    if ($null -eq (Get-Command $commandName -ErrorAction SilentlyContinue)) {
        throw "El comando $commandName no esta disponible. Este script requiere Windows Task Scheduler."
    }
}

$existingTask = Get-ScheduledTask `
    -TaskPath $TaskPath `
    -TaskName $TaskName `
    -ErrorAction SilentlyContinue
if ($null -eq $existingTask) {
    Write-Host "La tarea $TaskName no existe. No se modifico nada."
    exit 0
}

if (-not $Force -and -not $WhatIfPreference) {
    $answer = Read-Host "Escriba ELIMINAR para quitar la tarea $TaskName (los backups no se borraran)"
    if ($answer -cne "ELIMINAR") {
        Write-Host "Operacion cancelada. No se modifico ninguna tarea."
        exit 0
    }
}

if ($PSCmdlet.ShouldProcess("$TaskPath$TaskName", "Quitar tarea programada")) {
    try {
        Unregister-ScheduledTask `
            -TaskPath $TaskPath `
            -TaskName $TaskName `
            -Confirm:$false `
            -ErrorAction Stop
        Write-Host "Tarea quitada: $TaskName" -ForegroundColor Green
        Write-Host "Los backups y PostgreSQL no fueron modificados."
    }
    catch {
        throw "No se pudo quitar la tarea. Verifique los permisos de Windows. Detalle: $($_.Exception.Message)"
    }
}
elseif ($WhatIfPreference) {
    Write-Host "Modo WhatIf: no se quito ninguna tarea." -ForegroundColor Yellow
}
