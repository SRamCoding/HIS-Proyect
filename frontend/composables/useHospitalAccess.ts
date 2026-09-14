export function hospitalPermiso(path: string): string | null {
  if (path === '/app' || path === '/app/' || path === '/app/login') return null
  if (path.startsWith('/app/admision/programacion-medica')) return 'consulta_externa.programacion'
  if (path.startsWith('/app/consulta-externa/atenciones-medicas')) return 'consulta_externa.atenciones'
  if (path.startsWith('/app/consulta-externa/citas-por-confirmar')) return 'consulta_externa.confirmacion'
  if (path.startsWith('/app/consulta-externa/triaje')) return 'consulta_externa.triaje'
  if (path.startsWith('/app/admision/agendamiento')) return 'consulta_externa.agendamiento'
  const seccion = path.split('/')[2]?.replaceAll('-', '_')
  return seccion ? seccion : null
}

export function hospitalPuede(permisos: string[], codigo: string): boolean {
  return permisos.some(p => p === codigo || codigo.startsWith(p + '.'))
}
