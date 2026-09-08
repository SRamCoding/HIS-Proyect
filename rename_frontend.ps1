# rename_frontend.ps1
# Ejecutar desde: C:\Users\benja\ERP_HOSPITALARIO\frontend
# Antes de correr: hacer commit o backup, porque mueve/borra carpetas reales.

$ErrorActionPreference = "Stop"
Set-Location .\pages\app

Write-Host "== 1. Admision: gestion-pacientes -> admision ==" -ForegroundColor Cyan
if (Test-Path .\admision) {
    Remove-Item .\admision -Recurse -Force   # esta vacia, la limpiamos primero
}
Rename-Item .\gestion-pacientes admision

Write-Host "== 2. Imagenes: imagenologia -> imagenes ==" -ForegroundColor Cyan
Rename-Item .\imagenologia imagenes

Write-Host "== 3. Cobros -> fusionar dentro de Caja ==" -ForegroundColor Cyan
Move-Item .\cobros\cobro-por-paciente .\caja\cobro-por-paciente
Move-Item .\cobros\mi-caja .\caja\mi-caja
Remove-Item .\cobros -Recurse -Force

Write-Host "== 4. Reportes -> fusionar dentro de Informes ==" -ForegroundColor Cyan
New-Item -ItemType Directory -Path .\informes -Force | Out-Null
Move-Item .\reportes\reporte-medico .\informes\reporte-medico
Move-Item .\reportes\reportes-hospitalizacion .\informes\reportes-hospitalizacion
Remove-Item .\reportes -Recurse -Force

Write-Host "== 5. Telemedicina -> fusionar dentro de TeleSalud ==" -ForegroundColor Cyan
New-Item -ItemType Directory -Path .\telesalud -Force | Out-Null
Move-Item .\telemedicina\resumen-teleconsultas .\telesalud\resumen-teleconsultas
Move-Item .\telemedicina\guia-rapida-minsa .\telesalud\guia-rapida-minsa
if (Test-Path .\telemedicina\sala) {
    Move-Item .\telemedicina\sala .\telesalud\sala   # huerfana, no referenciada en el nav, se mueve igual por si se usa
}
Remove-Item .\telemedicina -Recurse -Force

Write-Host "== Listo. Estructura resultante: ==" -ForegroundColor Green
Get-ChildItem -Directory | Select-Object Name

Write-Host ""
Write-Host "PENDIENTE MANUAL: carpetas huerfanas que quedaron sin tocar (revisa si se usan antes de borrar):" -ForegroundColor Yellow
Write-Host "  - app\consulta-externa\citas"
Write-Host "  - app\emergencia\atencion"
Write-Host "  - app\emergencia\triaje"
Write-Host "  - app\nutricion (vacia, no es modulo del catalogo)"
Write-Host "  - app\sis-his (vacia, redundante con sis + his)"