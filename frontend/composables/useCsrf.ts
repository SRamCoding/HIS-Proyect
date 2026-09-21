// El backend expone csrf_token como cookie NO-httpOnly a proposito (ver
// backend/app/auth/router.py:_set_auth_cookies): el resto de la sesion
// (access_token, refresh_token) SI es httpOnly, invisible para JS, para que
// un XSS no pueda robarla. Este valor si se lee por JS y se reenvia como
// header en cada peticion que muta estado -- el patron de "doble
// presentacion" (double-submit cookie): un sitio ajeno puede hacer que el
// navegador de la victima MANDE la cookie sola, pero no puede LEERLA para
// reproducir el header, porque las cookies de otro origen no son legibles
// desde su propio JS.
export function leerCsrfToken(): string | null {
  if (typeof document === 'undefined') return null
  const match = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : null
}
