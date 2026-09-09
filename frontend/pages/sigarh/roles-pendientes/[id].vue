<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)

const rol = ref<any>(null)
const loading = ref(true)
const error = ref('')
const busy = ref(false)
const showRechazo = ref(false)
const motivo = ref('')

const cargar = async () => {
  loading.value = true; error.value = ''
  try { rol.value = await api<any>(`/sigarh/roles-pendientes/roles/${id.value}`) }
  catch (e: any) { error.value = e?.data?.detail || 'No se pudo cargar' }
  finally { loading.value = false }
}
const aprobar = async () => {
  if (!confirm('¿Aprobar este rol?')) return
  busy.value = true; error.value = ''
  try {
    await api(`/sigarh/roles-pendientes/roles/${id.value}/aprobar`, { method: 'POST' })
    router.push(`/sigarh/roles-pendientes?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo aprobar' }
  finally { busy.value = false }
}
const rechazar = async () => {
  if (motivo.value.trim().length < 5) { error.value = 'El motivo del rechazo es obligatorio'; return }
  busy.value = true; error.value = ''
  try {
    await api(`/sigarh/roles-pendientes/roles/${id.value}/rechazar`, { method: 'POST', body: { motivo: motivo.value } })
    router.push(`/sigarh/roles-pendientes?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo rechazar' }
  finally { busy.value = false }
}
onMounted(cargar)
</script>

<template>
  <div class="rt-wrap">
    <div class="mb-6">
      <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/roles-pendientes?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Roles Pendientes</NuxtLink>
        <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
        <span style="color: var(--ink)">Revisión</span>
      </div>
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--amber-soft)">
            <UIcon name="i-heroicons-clipboard-document-check" class="w-6 h-6" style="color: var(--amber)" />
          </div>
          <div>
            <h1 class="page-title">Revisar rol</h1>
            <p class="page-subtitle">{{ rol ? (rol.servicio_nombre || 'Rol') : '' }}</p>
          </div>
        </div>
        <div v-if="rol" class="flex items-center gap-2">
          <button class="btn-outline" :disabled="busy" @click="showRechazo = !showRechazo" style="border-color: var(--alert); color: var(--alert)">Rechazar</button>
          <button class="btn-primary" :disabled="busy" @click="aprobar">
            <UIcon name="i-heroicons-check" class="w-4 h-4" /> Aprobar
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-banner" style="margin-bottom: 1rem">{{ error }}</div>

    <div v-if="showRechazo" class="rt-card">
      <label class="form-label">Motivo del rechazo <span class="required">*</span></label>
      <textarea v-model="motivo" rows="3" class="input-clinical" style="padding-left: 0.75rem" placeholder="Explica qué debe corregirse..." />
      <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.6rem">
        <button class="btn-cancel" @click="showRechazo = false">Cancelar</button>
        <button class="btn-primary" style="background: var(--alert)" :disabled="busy" @click="rechazar">Confirmar rechazo</button>
      </div>
    </div>

    <div v-if="loading" class="rt-card" style="text-align:center; padding: 3rem">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--amber)" />
    </div>
    <SRolDetalle v-else-if="rol" :rol="rol" />
  </div>
</template>

<style scoped>
.rt-wrap { max-width: 1000px; margin: 0 auto; padding: 1.5rem 2rem; }
.rt-card { background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1rem 1.25rem; margin-bottom: 1rem; }
</style>
