<template>
  <div class="archivo-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-user-group" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <p class="breadcrumb-label" style="color: var(--ink-soft); font-size: 0.75rem;">Archivo Clínico</p>
          <h1 class="page-title">Personal de Archivo</h1>
          <p class="page-subtitle">Cuentas con rol de archivo en este hospital.</p>
        </div>
      </div>
      <button class="btn-secondary" :disabled="loading" @click="cargar">
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
        Actualizar
      </button>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>

    <section class="panel">
      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <div v-else class="table-responsive">
        <table class="lab-table">
          <thead><tr><th>Cuenta</th><th>Empleado</th><th>Perfil</th><th>Estado</th></tr></thead>
          <tbody>
            <tr v-for="p in personal" :key="p.id">
              <td><span class="cell-name">{{ p.name }}</span><span class="cell-sub">{{ p.email }}</span></td>
              <td>{{ p.empleado_nombre || '— sin vincular' }}<span v-if="p.empleado_dni" class="cell-sub"> DNI {{ p.empleado_dni }}</span></td>
              <td>{{ p.perfil_nombre || '— sin perfil' }}</td>
              <td><span class="badge" :class="p.is_active ? 'badge-ok' : 'badge-off'">{{ p.is_active ? 'Activo' : 'Inactivo' }}</span></td>
            </tr>
            <tr v-if="!personal.length"><td colspan="4" style="text-align:center;color:var(--ink-soft)">No hay cuentas con rol de archivo registradas en este hospital.</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { api } = useApi()
const personal = ref<any[]>([])
const loading = ref(false)
const error = ref('')

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    personal.value = await api('/app/archivo-clinico/personal-archivo')
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar el personal de archivo'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.archivo-container { max-width: 1100px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.page-subtitle { font-size: 0.8125rem; color: var(--ink-soft); margin: 0.125rem 0 0 0; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; box-shadow: var(--shadow-sm); }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.cell-name { display: block; color: var(--ink); font-weight: 500; }
.cell-sub { display: block; color: var(--ink-soft); font-size: 0.75rem; }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-off { color: var(--alert); background: var(--alert-soft); }
@media (max-width: 768px) {
  .archivo-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
}
</style>
