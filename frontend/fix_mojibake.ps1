# fix_mojibake.ps1
# Revierte la corrupcion de encoding causada por Get-Content sin -Encoding UTF8
# seguido de Set-Content -Encoding utf8 (PowerShell 5.1 Windows).
#
# Tecnica: el texto actual en disco es UTF-8 valido, pero cada caracter con tilde
# quedo "doble-codificado". Se revierte re-mapeando el string actual como si
# fueran bytes Windows-1252, y decodificando esos bytes de vuelta como UTF-8.
#
# USAR UNA SOLA VEZ por archivo. Correrlo dos veces vuelve a corromper.
#
# Ejecutar dos veces: una desde frontend/, otra desde backend/ (ver abajo).

param(
    [Parameter(Mandatory=$true)]
    [string[]]$Files
)

$latin1 = [System.Text.Encoding]::GetEncoding(1252)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

foreach ($f in $Files) {
    if (-not (Test-Path -LiteralPath $f)) {
        Write-Host "SALTADO (no existe): $f" -ForegroundColor Yellow
        continue
    }

    $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $f))
    $corruptedText = [System.Text.Encoding]::UTF8.GetString($bytes)

    # Solo re-procesar si hay indicios de mojibake tipico (Ã, Â, etc.)
    if ($corruptedText -notmatch "[ÃÂ]") {
        Write-Host "SIN CAMBIOS (no se detecto mojibake): $f" -ForegroundColor DarkGray
        continue
    }

    $originalBytes = $latin1.GetBytes($corruptedText)
    $fixedText = [System.Text.Encoding]::UTF8.GetString($originalBytes)

    [System.IO.File]::WriteAllText((Resolve-Path -LiteralPath $f), $fixedText, $utf8NoBom)
    Write-Host "CORREGIDO: $f" -ForegroundColor Green
}