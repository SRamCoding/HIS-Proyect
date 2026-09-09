// Normaliza los errores del backend SIGARH.
// El backend responde SIEMPRE con { ok:false, status, message, errors? }
// (ver backend/app/core/exceptions.py). Antes se leía `detail`, que nunca existe.
export const apiErr = (e: any, fallback = 'Ocurrió un error inesperado'): string => {
  const d = e?.data ?? e?.response?._data ?? e

  // 422 de validación: { errors: { campo: [msg, ...] } }
  if (d?.errors && typeof d.errors === 'object') {
    const msgs = Object.values(d.errors)
      .flat()
      .map((m: any) => String(m).replace(/^Value error,\s*/, ''))
      .filter(Boolean)
    if (msgs.length) return msgs.join(' · ')
  }

  // HTTPException del backend: { message: "..." }
  if (typeof d?.message === 'string' && d.message && d.message !== 'Error de validación') {
    return d.message
  }

  // Formato FastAPI por defecto (por si algún endpoint no pasa por el handler)
  if (typeof d?.detail === 'string' && d.detail) return d.detail
  if (Array.isArray(d?.detail)) {
    const s = d.detail
      .map((x: any) => String(x?.msg || '').replace(/^Value error,\s*/, ''))
      .filter(Boolean)
      .join(' · ')
    if (s) return s
  }

  return fallback
}
