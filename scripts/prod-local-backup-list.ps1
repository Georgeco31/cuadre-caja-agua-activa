Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BackupDirectory = Join-Path $RepoRoot "backups/postgres"

if (-not (Test-Path -LiteralPath $BackupDirectory -PathType Container)) {
    Write-Host "No existe todavia la carpeta de backups: $BackupDirectory"
    exit 0
}

$backups = @(
    Get-ChildItem -LiteralPath $BackupDirectory -File -Filter "*.dump" |
        Sort-Object -Property LastWriteTimeUtc -Descending
)

if ($backups.Count -eq 0) {
    Write-Host "No hay backups PostgreSQL en: $BackupDirectory"
    exit 0
}

$rows = foreach ($backup in $backups) {
    [PSCustomObject]@{
        Fecha = $backup.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
        Nombre = $backup.Name
        Tamano = if ($backup.Length -ge 1MB) {
            "{0:N2} MB" -f ($backup.Length / 1MB)
        }
        elseif ($backup.Length -ge 1KB) {
            "{0:N2} KB" -f ($backup.Length / 1KB)
        }
        else {
            "$($backup.Length) bytes"
        }
        SHA256 = if (Test-Path -LiteralPath "$($backup.FullName).sha256" -PathType Leaf) {
            "Si"
        }
        else {
            "No"
        }
        Metadata = if (Test-Path -LiteralPath "$($backup.FullName).json" -PathType Leaf) {
            "Si"
        }
        else {
            "No"
        }
    }
}

Write-Host "Backups PostgreSQL: $BackupDirectory"
$rows | Format-Table -AutoSize
