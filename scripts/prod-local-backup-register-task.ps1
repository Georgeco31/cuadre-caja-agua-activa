[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Medium")]
param(
    [ValidateNotNullOrEmpty()]
    [string]$TaskName = "AguaActivaERP-BackupDiario",

    [ValidatePattern("^(?:[01]\d|2[0-3]):[0-5]\d$")]
    [string]$Time = "23:30"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BackupScript = Join-Path $RepoRoot "scripts/prod-local-backup-db.ps1"
$TaskPath = "\"

foreach ($commandName in @(
    "Get-ScheduledTask",
    "New-ScheduledTaskAction",
    "New-ScheduledTaskPrincipal",
    "New-ScheduledTaskSettingsSet",
    "New-ScheduledTaskTrigger",
    "Register-ScheduledTask"
)) {
    if ($null -eq (Get-Command $commandName -ErrorAction SilentlyContinue)) {
        throw "El comando $commandName no esta disponible. Este script requiere Windows Task Scheduler."
    }
}

if (-not (Test-Path -LiteralPath $BackupScript -PathType Leaf)) {
    throw "No existe el script de backup requerido: $BackupScript"
}

if ($BackupScript.Contains('"')) {
    throw "La ruta del repositorio contiene comillas y no es segura para la tarea programada."
}

try {
    $existingTask = Get-ScheduledTask `
        -TaskPath $TaskPath `
        -TaskName $TaskName `
        -ErrorAction Stop
}
catch {
    if ($_.FullyQualifiedErrorId -like "CmdletizationQuery_NotFound*") {
        $existingTask = $null
    }
    else {
        throw "No se pudo consultar si la tarea $TaskName ya existe. Ejecute PowerShell con permisos suficientes. Detalle: $($_.Exception.Message)"
    }
}

if ($null -ne $existingTask) {
    throw "La tarea $TaskName ya existe. Revise su estado o quitela de forma explicita antes de registrarla otra vez."
}

$runAt = [DateTime]::Today.Add(
    [TimeSpan]::ParseExact(
        $Time,
        "hh\:mm",
        [Globalization.CultureInfo]::InvariantCulture
    )
)
$powerShellExecutable = Join-Path `
    $env:SystemRoot `
    "System32/WindowsPowerShell/v1.0/powershell.exe"
$arguments = '-NoProfile -ExecutionPolicy Bypass -File "{0}"' -f $BackupScript
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent().Name

Write-Host "Preparacion de tarea diaria: $TaskName a las $Time"
Write-Host "Programa: $powerShellExecutable"
Write-Host "Script: $BackupScript"
Write-Warning "Docker Desktop debe estar iniciado y disponible para el usuario $currentUser."
Write-Warning "La tarea usa la sesion interactiva y no guarda contrasenas."
Write-Warning "Si la PC esta apagada o el usuario no tiene una sesion activa a esa hora, el backup no se ejecutara."
Write-Warning "Un backup en el mismo disco no protege ante dano fisico, robo o perdida total del equipo."
Write-Host "Copie periodicamente los backups importantes a un disco externo o ubicacion segura."

if ($PSCmdlet.ShouldProcess(
    "$TaskPath$TaskName",
    "Registrar backup diario a las $Time"
)) {
    try {
        $action = New-ScheduledTaskAction `
            -Execute $powerShellExecutable `
            -Argument $arguments `
            -WorkingDirectory $RepoRoot
        $trigger = New-ScheduledTaskTrigger -Daily -At $runAt
        $principal = New-ScheduledTaskPrincipal `
            -UserId $currentUser `
            -LogonType Interactive `
            -RunLevel Limited
        $settings = New-ScheduledTaskSettingsSet `
            -MultipleInstances IgnoreNew `
            -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
            -StartWhenAvailable `
            -RestartCount 3 `
            -RestartInterval (New-TimeSpan -Minutes 5) `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries

        Register-ScheduledTask `
            -TaskPath $TaskPath `
            -TaskName $TaskName `
            -Action $action `
            -Trigger $trigger `
            -Principal $principal `
            -Settings $settings `
            -Description "Backup diario seguro de PostgreSQL para Agua Activa ERP." `
            -ErrorAction Stop | Out-Null
        Write-Host "Tarea registrada: $TaskName" -ForegroundColor Green
        Write-Host "La tarea no se ha ejecutado ahora; solo quedo programada."
    }
    catch {
        throw "No se pudo registrar la tarea. Verifique permisos, la sesion de Windows y Docker Desktop. Detalle: $($_.Exception.Message)"
    }
}
elseif ($WhatIfPreference) {
    Write-Host "Modo WhatIf: no se registro ninguna tarea." -ForegroundColor Yellow
}
