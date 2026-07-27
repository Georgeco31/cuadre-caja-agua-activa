Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$EvidenceDirectory = Join-Path $RepoRoot "backups/restore-tests"

if (-not (Test-Path -LiteralPath $EvidenceDirectory -PathType Container)) {
    Write-Host "No existe todavia la carpeta de evidencias: $EvidenceDirectory"
    exit 0
}

$evidenceFiles = @(
    Get-ChildItem -LiteralPath $EvidenceDirectory -File `
        -Filter "restore-test-*.json" |
        Sort-Object -Property LastWriteTimeUtc -Descending
)

if ($evidenceFiles.Count -eq 0) {
    Write-Host "No hay evidencias de restauracion en: $EvidenceDirectory"
    exit 0
}

$rows = foreach ($evidenceFile in $evidenceFiles) {
    try {
        $evidence = Get-Content -Raw -LiteralPath $evidenceFile.FullName |
            ConvertFrom-Json

        $createdAt = [DateTimeOffset]::MinValue
        $dateText = if (
            [DateTimeOffset]::TryParse(
                [string]$evidence.created_at,
                [ref]$createdAt
            )
        ) {
            $createdAt.ToLocalTime().ToString("yyyy-MM-dd HH:mm:ss")
        }
        else {
            "Fecha invalida"
        }

        [PSCustomObject]@{
            Fecha = $dateText
            Archivo = $evidenceFile.Name
            Backup = [string]$evidence.backup_file
            Estado = [string]$evidence.restore_status
            Alembic = [string]$evidence.alembic_version_restored
            Cleanup = [string]$evidence.cleanup_status
        }
    }
    catch {
        [PSCustomObject]@{
            Fecha = $evidenceFile.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
            Archivo = $evidenceFile.Name
            Backup = "No disponible"
            Estado = "JSON_INVALIDO"
            Alembic = "No disponible"
            Cleanup = "No disponible"
        }
    }
}

Write-Host "Evidencias de restauracion controlada: $EvidenceDirectory"
$rows | Format-List Fecha, Archivo, Backup, Estado, Alembic, Cleanup
