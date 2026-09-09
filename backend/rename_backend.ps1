# rename_backend.ps1
# Ejecutar desde: C:\Users\benja\ERP_HOSPITALARIO\backend
# Antes de correr: hacer commit o backup. Despues de correrlo, hay que
# actualizar a mano el archivo donde se registran los routers (main.py o
# equivalente) para que apunte a las rutas/nombres nuevos.

$ErrorActionPreference = "Stop"
Set-Location .\app\hospital

Write-Host "== 1. gestion_pacientes -> admision ==" -ForegroundColor Cyan
Rename-Item .\gestion_pacientes admision

Write-Host "== 2. imagenologia -> imagenes ==" -ForegroundColor Cyan
Rename-Item .\imagenologia imagenes

Write-Host "== 3. cobros -> fusionar logica dentro de caja (manual) ==" -ForegroundColor Yellow
Write-Host "   No se puede fusionar router.py automaticamente sin romper el codigo."
Write-Host "   Copia manualmente los endpoints de hospital\cobros\router.py hacia"
Write-Host "   hospital\caja\router.py bajo el mismo prefix '/caja', y borra la carpeta:"
Write-Host "   Remove-Item .\cobros -Recurse -Force"

Write-Host "== 4. reportes -> fusionar logica dentro de informes (crear modulo nuevo) ==" -ForegroundColor Yellow
Write-Host "   No existe carpeta 'informes' todavia. Pasos sugeridos:"
Write-Host "   1) Copiar hospital\reportes como base: Copy-Item .\reportes .\informes -Recurse"
Write-Host "   2) Editar .\informes\router.py: cambiar prefix a '/informes'"
Write-Host "   3) Editar .\informes\models.py/schemas.py/service.py: revisar nombres de clases"
Write-Host "   4) Remove-Item .\reportes -Recurse -Force"

Write-Host "== 5. telemedicina -> renombrar a telesalud ==" -ForegroundColor Cyan
Rename-Item .\telemedicina telesalud

Write-Host ""
Write-Host "== Listo (parcial). Revisa los pasos manuales de arriba para cobros/reportes. ==" -ForegroundColor Green
Get-ChildItem -Directory | Select-Object Name

Write-Host ""
Write-Host "IMPORTANTE: busca donde se registran los routers (usualmente en" -ForegroundColor Yellow
Write-Host "backend\main.py o backend\app\api.py) y actualiza los imports:"
Write-Host "  from app.hospital.gestion_pacientes.router  ->  from app.hospital.admision.router"
Write-Host "  from app.hospital.imagenologia.router       ->  from app.hospital.imagenes.router"
Write-Host "  from app.hospital.telemedicina.router       ->  from app.hospital.telesalud.router"
Write-Host "  from app.hospital.cobros.router             ->  eliminar / fusionar en caja"
Write-Host "  from app.hospital.reportes.router           ->  from app.hospital.informes.router"
Write-Host ""
Write-Host "Tambien revisa dentro de cada router.py renombrado si el codigo interno"
Write-Host "(nombres de tablas, imports relativos, tags de Swagger) sigue diciendo"
Write-Host "'gestion_pacientes' / 'imagenologia' / 'telemedicina' y actualizalo."