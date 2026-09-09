# fix_gestion_pacientes_refs.ps1
# Ejecutar desde: C:\Users\benja\ERP_HOSPITALARIO\backend
# Reemplaza las referencias del modulo viejo 'gestion_pacientes' por 'admision'
# SOLO en los archivos que sabemos que las tienen (no toca el resto del repo).

$ErrorActionPreference = "Stop"

$files = @(
    ".\app\hospital\archivo_clinico\models.py",
    ".\app\hospital\archivo_clinico\service.py",
    ".\app\hospital\consulta_externa\service.py",
    ".\app\hospital\emergencia\service.py",
    ".\app\hospital\hospitalizacion\service.py",
    ".\app\hospital\laboratorio\service.py",
    ".\migrations\env.py",
    ".\tests\test_archivo_clinico.py",
    ".\tests\test_laboratorio.py"
)

foreach ($f in $files) {
    if (-not (Test-Path $f)) {
        Write-Host "SALTADO (no existe): $f" -ForegroundColor Yellow
        continue
    }
    $content = Get-Content -Path $f -Raw

    $before = $content
    $content = $content -replace "app\.hospital\.gestion_pacientes\.models", "app.hospital.admision.models"
    $content = $content -replace 'module_code="gestion_pacientes"', 'module_code="admision"'

    if ($content -ne $before) {
        Set-Content -Path $f -Value $content -Encoding utf8 -NoNewline
        Write-Host "OK - actualizado: $f" -ForegroundColor Green
    } else {
        Write-Host "SIN CAMBIOS: $f" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "== Verificacion final: no debe quedar ninguna coincidencia ==" -ForegroundColor Cyan
Get-ChildItem -Recurse -Filter *.py -Exclude __pycache__ | Select-String -Pattern "gestion_pacientes" | Format-List Path, LineNumber, Line