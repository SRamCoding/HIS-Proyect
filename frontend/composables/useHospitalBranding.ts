interface HospitalBranding {
  id: string
  name: string
  logo_url: string | null
  is_active: boolean
  hospital_level: string | null
}
export function useHospitalBranding() {
  const route = useRoute()
  const config = useRuntimeConfig()
  const hostname = useRequestURL().hostname
  const explicitTenant = computed(() => typeof route.query.tenant === 'string' ? route.query.tenant : '')
  const key = computed(() => `hospital-branding:${hostname}:${explicitTenant.value}`)
  const result = useAsyncData<HospitalBranding | null>(key, async () => {
    const base = import.meta.server ? config.internalApiUrl : config.public.apiUrl
    let id = explicitTenant.value
    if (!id) {
      const resolved = await $fetch<{ tenant_id: string | null }>(`${base}/auth/resolver-dominio`, { query: { domain: hostname } })
      id = resolved.tenant_id || ''
    }
    if (!id) return null
    return await $fetch<HospitalBranding>(`${base}/auth/tenant-publico/${encodeURIComponent(id)}`)
  }, { dedupe: 'defer', default: () => null })
  return { hospital: result.data, pending: result.pending, brandingError: result.error,
    tenantId: computed(() => result.data.value?.id || explicitTenant.value), refreshBranding: result.refresh }
}
