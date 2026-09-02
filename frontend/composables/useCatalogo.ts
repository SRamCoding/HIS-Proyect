// composables/useCatalogo.ts
export const useCatalogo = <T extends { id: string }>(endpoint: string) => {
  const { api } = useApi()
  const route = useRoute()
  const tenantId = computed(() => route.query.tenant as string || '')

  const items = ref<T[]>([])
  const loading = ref(true)
  const error = ref('')
  const saving = ref(false)
  const saveError = ref('')
  const showModal = ref(false)
  const editingId = ref<string | null>(null)

  const cargar = async () => {
    loading.value = true
    error.value = ''
    try {
      items.value = await api<T[]>(endpoint, {
        headers: { 'X-Tenant-ID': tenantId.value }
      })
    } catch (e: any) {
      error.value = e?.data?.detail || 'Error de conexion'
    } finally {
      loading.value = false
    }
  }

  const guardar = async (form: Record<string, any>) => {
    saving.value = true
    saveError.value = ''
    try {
      if (editingId.value) {
        const updated = await api<T>(`${endpoint}/${editingId.value}`, {
          method: 'PATCH',
          body: form,
        })
        const idx = items.value.findIndex(i => i.id === editingId.value)
        if (idx !== -1) items.value[idx] = updated
      } else {
        const created = await api<T>(endpoint, {
          method: 'POST',
          body: form,
        })
        items.value.unshift(created)
      }
      showModal.value = false
      editingId.value = null
      return true
    } catch (e: any) {
      saveError.value = e?.data?.detail || 'No se pudo guardar'
      return false
    } finally {
      saving.value = false
    }
  }

  const eliminar = async (id: string) => {
    if (!confirm('¿Eliminar este registro?')) return
    try {
      await api(`${endpoint}/${id}`, { method: 'DELETE' })
      items.value = items.value.filter(i => i.id !== id)
    } catch (e: any) {
      error.value = e?.data?.detail || 'No se pudo eliminar'
    }
  }

  const abrirCrear = () => {
    editingId.value = null
    saveError.value = ''
    showModal.value = true
  }

  const abrirEditar = (id: string) => {
    editingId.value = id
    saveError.value = ''
    showModal.value = true
  }

  onMounted(cargar)

  return {
    items, loading, error,
    saving, saveError, showModal, editingId,
    cargar, guardar, eliminar,
    abrirCrear, abrirEditar,
    tenantId,
  }
}