export interface HospitalPreferences {
  collapsedSidebar: boolean
  compactTables: boolean
  reduceMotion: boolean
}

export const useHospitalPreferences = () => {
  const auth = useAuthStore()
  const preferences = useState<HospitalPreferences>('hospital-preferences', () => defaults())
  const storageError = useState('hospital-preferences-error', () => '')
  const storageKey = computed(() => {
    const user = auth.user
    return user?.id && user?.tenant_id ? `hospital-preferences:v1:${user.tenant_id}:${user.id}` : ''
  })
  function defaults(): HospitalPreferences {
    return { collapsedSidebar: false, compactTables: false, reduceMotion: false }
  }
  function normalize(value: any): HospitalPreferences {
    return {
      collapsedSidebar: value?.collapsedSidebar === true,
      compactTables: value?.compactTables === true,
      reduceMotion: value?.reduceMotion === true,
    }
  }
  function load() {
    preferences.value = defaults()
    storageError.value = ''
    if (!import.meta.client || !storageKey.value) return
    try {
      preferences.value = normalize(JSON.parse(localStorage.getItem(storageKey.value) || '{}'))
    } catch {
      storageError.value = 'No se pudieron leer las preferencias. Puedes restablecerlas o guardarlas nuevamente.'
    }
  }
  function save(value: HospitalPreferences): boolean {
    storageError.value = ''
    if (!import.meta.client || !storageKey.value) {
      storageError.value = 'No se pudo identificar tu cuenta y hospital para guardar las preferencias.'
      return false
    }
    try {
      const next = normalize(value)
      localStorage.setItem(storageKey.value, JSON.stringify(next))
      preferences.value = next
      return true
    } catch {
      storageError.value = 'El navegador no permitió guardar las preferencias. Revisa la disponibilidad del almacenamiento local.'
      return false
    }
  }
  return { preferences, storageError, storageKey, defaults, load, save }
}
