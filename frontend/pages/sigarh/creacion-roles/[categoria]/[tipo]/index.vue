<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const { modalidadLabel, tipoValido, periodoLabel, estadoRol } = useRolesTurno()
const tenantId = computed(() => route.query.tenant as string || '')
const categoria = computed(() => route.params.categoria as string)
const tipo = computed(() => route.params.tipo as string)

interface Item {
  id: string; servicio_nombre: string | null; departamento_nombre: string | null
  mes: number; anio: number; status: string; total_actividades: number
  total_empleados: number; rejection_reason: string | null; created_at: string
}
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')

const cargar = async () => {
  loading.value = true; error.value = ''
  try {
    items.value = await api<Item[]>(`/sigarh/creacion-roles/roles?categoria=${categoria.value}&tipo=${tipo.value}`)
  } catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
const eliminar = async (it: Item) => {
  if (!confirm('¿Eliminar este rol en borrador?')) return
  try {
    await api(`/sigarh/creacion-roles/roles/${it.id}`, { method: 'DELETE' })
    items.value = items.value.filter(i => i.id !== it.id)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}
onMounted(cargar)
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <h1 class="page-title">Creación de Roles</h1>
          <p class="page-subtitle">{{ tipoValido(categoria, tipo) ? modalidadLabel(categoria, tipo) : 'Modalidad no válida' }}</p>
        </div>
      </div>
      <NuxtLink v-if="tipoValido(categoria, tipo)" :to="`/sigarh/creacion-roles/${categoria}/${tipo}/create?tenant=${tenantId}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Rol
      </NuxtLink>
    </div>

    <div v-if="!tipoValido(categoria, tipo)" class="sigarh-table-state">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
      <p style="color: var(--alert)">La modalidad "{{ categoria }}/{{ tipo }}" no existe.</p>
    </div>

    <div v-else class="sigarh-table-container">
      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" />
        <p style="color: var(--ink-soft)">Cargando roles...</p>
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button @click="cargar" class="btn-outline">Reintentar</button>
      </div>
      <div v-else-if="!items.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-document-plus" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">Sin roles en borrador</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0">Crea un rol y agrégale personal, actividades y turnos</p>
        </div>
        <NuxtLink :to="`/sigarh/creacion-roles/${categoria}/${tipo}/create?tenant=${tenantId}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Rol
        </NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th style="width: 22%">Servicio</th>
              <th style="width: 18%">Departamento</th>
              <th style="width: 14%">Período</th>
              <th style="width: 10%">Personal</th>
              <th style="width: 10%">Activid.</th>
              <th style="width: 14%">Estado</th>
              <th style="width: 12%; text-align: right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="it in items" :key="it.id">
              <td class="sigarh-item-name">{{ it.servicio_nombre || '—' }}</td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ it.departamento_nombre || '—' }}</td>
              <td style="font-size: 0.8125rem">{{ periodoLabel(it.mes, it.anio) }}</td>
              <td style="font-family: monospace; color: var(--ink-soft)">{{ it.total_empleados }}</td>
              <td style="font-family: monospace; color: var(--ink-soft)">{{ it.total_actividades }}</td>
              <td>
                <span class="badge" :class="estadoRol(it.status).badge">{{ estadoRol(it.status).label }}</span>
                <div v-if="it.status === 'rejected' && it.rejection_reason" style="font-size: 0.6875rem; color: var(--alert); margin-top: 0.2rem">{{ it.rejection_reason }}</div>
              </td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/creacion-roles/${categoria}/${tipo}/${it.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Abrir">
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" />
                  </NuxtLink>
                  <button class="sigarh-action-btn danger" title="Eliminar" @click="eliminar(it)">
                    <UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">{{ items.length }} rol(es) en borrador o rechazados</div>
      </div>
    </div>
  </div>
</template>
