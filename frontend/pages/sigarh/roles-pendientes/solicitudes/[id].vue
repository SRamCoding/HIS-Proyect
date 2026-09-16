<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const { estadoSolicitud, diasLabel, tipoLabel, categoriaLabel } = useRolesTurno()
const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)

const sol = ref<any>(null)
const loading = ref(true)
const error = ref('')
const busy = ref(false)
const showRechazo = ref(false)
const motivo = ref('')

const roleType = (rt: string | null) => {
  if (!rt) return '—'
  const [cat, tipo] = rt.split('/')
  return `${categoriaLabel(cat)} · ${tipoLabel(tipo)}`
}
const cargar = async () => {
  loading.value = true; error.value = ''
  try { sol.value = await api<any>(`/sigarh/roles-pendientes/solicitudes-modificacion/${id.value}`) }
  catch (e: any) { error.value = apiErr(e, 'No se pudo cargar') }
  finally { loading.value = false }
}
const aprobar = async () => {
  if (!confirm('¿Aprobar la solicitud? Se incorporará al empleado y su programación al rol.')) return
  busy.value = true; error.value = ''
  try {
    await api(`/sigarh/roles-pendientes/solicitudes-modificacion/${id.value}/aprobar`, { method: 'POST' })
    router.push(`/sigarh/roles-pendientes/solicitudes?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo aprobar') }
  finally { busy.value = false }
}
const rechazar = async () => {
  if (motivo.value.trim().length < 5) { error.value = 'El motivo es obligatorio'; return }
  busy.value = true; error.value = ''
  try {
    await api(`/sigarh/roles-pendientes/solicitudes-modificacion/${id.value}/rechazar`, { method: 'POST', body: { motivo: motivo.value } })
    router.push(`/sigarh/roles-pendientes/solicitudes?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo rechazar') }
  finally { busy.value = false }
}
onMounted(cargar)
</script>

<template>
  <div class="rt-wrap">
    <div class="mb-6">
      <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/roles-pendientes/solicitudes?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Solicitudes</NuxtLink>
        <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
        <span style="color: var(--ink)">Detalle</span>
      </div>
      <div class="flex items-center justify-between flex-wrap gap-3">
        <h1 class="page-title">Solicitud de modificación</h1>
        <div v-if="sol && sol.status === 'pendiente'" class="flex items-center gap-2">
          <button class="btn-outline" style="border-color: var(--alert); color: var(--alert)" :disabled="busy" @click="showRechazo = !showRechazo">Rechazar</button>
          <button class="btn-primary" :disabled="busy" @click="aprobar"><UIcon name="i-heroicons-check" class="w-4 h-4" /> Aprobar</button>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-banner" style="margin-bottom: 1rem">{{ error }}</div>

    <div v-if="showRechazo" class="rt-card">
      <label class="form-label">Motivo del rechazo <span class="required">*</span></label>
      <textarea v-model="motivo" rows="3" class="input-clinical" style="padding-left: 0.75rem" />
      <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.6rem">
        <button class="btn-cancel" @click="showRechazo = false">Cancelar</button>
        <button class="btn-primary" style="background: var(--alert)" :disabled="busy" @click="rechazar">Confirmar rechazo</button>
      </div>
    </div>

    <div v-if="loading" class="rt-card" style="text-align:center; padding: 3rem">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--purple)" />
    </div>

    <template v-else-if="sol">
      <div class="rt-card srd-header">
        <div><span class="srd-k">Modalidad</span><span class="srd-v">{{ roleType(sol.role_type) }}</span></div>
        <div><span class="srd-k">Período</span><span class="srd-v">{{ sol.rol_periodo || '—' }}</span></div>
        <div><span class="srd-k">Servicio</span><span class="srd-v">{{ sol.rol_servicio_nombre || '—' }}</span></div>
        <div><span class="srd-k">Empleado</span><span class="srd-v">{{ sol.empleado_nombre || '—' }}</span></div>
        <div><span class="srd-k">Estado</span><span class="srd-v"><span class="badge" :class="estadoSolicitud(sol.status).badge">{{ estadoSolicitud(sol.status).label }}</span></span></div>
        <div><span class="srd-k">Solicitado por</span><span class="srd-v">{{ sol.requested_by || '—' }}</span></div>
      </div>

      <div class="rt-card">
        <div class="rt-card-title"><UIcon name="i-heroicons-chat-bubble-bottom-center-text" class="w-4 h-4" /> Motivo</div>
        <p style="font-size: 0.85rem; color: var(--ink); white-space: pre-wrap">{{ sol.motivo }}</p>
      </div>

      <div class="rt-card">
        <div class="rt-card-title"><UIcon name="i-heroicons-calendar-days" class="w-4 h-4" /> Programación propuesta</div>
        <div v-if="!(sol.schedule_data?.actividades?.length)" style="font-size: 0.8rem; color: var(--ink-soft)">Sin actividades propuestas.</div>
        <div v-for="(act, i) in (sol.schedule_data?.actividades || [])" :key="i" class="srd-act">
          <div class="srd-act-name"><UIcon name="i-heroicons-bolt" class="w-3.5 h-3.5" style="color: var(--orange)" /> Actividad {{ i + 1 }}</div>
          <div v-for="(t, j) in (act.turnos || [])" :key="j" class="srd-turno">
            <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" style="color: var(--purple)" />
            <span class="srd-dias">{{ diasLabel(t.dias_semana) }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.rt-wrap { max-width: 900px; margin: 0 auto; padding: 1.5rem 2rem; }
.rt-card { background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1rem 1.25rem; margin-bottom: 1rem; }
.rt-card-title { display: flex; align-items: center; gap: 0.5rem; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.6rem; }
.srd-header { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.75rem; }
.srd-k { display: block; font-size: 0.68rem; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.04em; }
.srd-v { display: block; font-size: 0.9rem; font-weight: 700; color: var(--ink); }
.srd-act { background: var(--mist); border-radius: 6px; padding: 0.6rem; margin-bottom: 0.4rem; }
.srd-act-name { display: flex; align-items: center; gap: 0.4rem; font-weight: 600; font-size: 0.82rem; margin-bottom: 0.35rem; }
.srd-turno { display: flex; align-items: center; gap: 0.5rem; font-size: 0.78rem; padding: 0.25rem 0.4rem; background: var(--paper); border: 1px solid var(--line); border-radius: 5px; margin-bottom: 0.25rem; }
.srd-dias { color: var(--ink-soft); font-size: 0.75rem; }
</style>
