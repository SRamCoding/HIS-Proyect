// Etiqueta legible para el `role` crudo que devuelve el backend, usada donde
// se necesite mostrar el rol al usuario (ej. aviso post-login). Catálogo real
// de SystemRole panel='app': administrador, enfermera, farmaceutico,
// laboratorista, cajero, tuasis, medico (ver backend/app/admin/seeder_niveles.py
// y seed real). Los roles de panel admin/sigarh son más libres, de ahí el
// fallback que capitaliza en vez de fallar.
const ROLE_LABELS: Record<string, string> = {
  administrador: 'Administrador',
  medico: 'Médico',
  enfermera: 'Enfermera',
  farmaceutico: 'Farmacéutico',
  laboratorista: 'Laboratorista',
  cajero: 'Cajero',
  tuasis: 'TUASIS',
  rrhh: 'Recursos Humanos',
}

export function roleLabel(role: string | null | undefined): string {
  if (!role) return 'Usuario'
  return ROLE_LABELS[role] || role.charAt(0).toUpperCase() + role.slice(1)
}
