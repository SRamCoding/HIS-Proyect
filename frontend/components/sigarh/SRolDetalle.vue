<template>
  <div>
    <div class="srd-header">
      <div><span class="srd-k">Modalidad</span><span class="srd-v">{{ modalidadLabel(rol.categoria_personal, rol.tipo_rol) }}</span></div>
      <div><span class="srd-k">Departamento</span><span class="srd-v">{{ rol.departamento_nombre || '—' }}</span></div>
      <div><span class="srd-k">Servicio</span><span class="srd-v">{{ rol.servicio_nombre || '—' }}</span></div>
      <div><span class="srd-k">Período</span><span class="srd-v">{{ periodoLabel(rol.mes, rol.anio) }}</span></div>
      <div><span class="srd-k">Personal</span><span class="srd-v">{{ rol.total_empleados }}</span></div>
      <div><span class="srd-k">Actividades</span><span class="srd-v">{{ rol.total_actividades }}</span></div>
      <div><span class="srd-k">Turnos</span><span class="srd-v">{{ rol.total_turnos }}</span></div>
    </div>

    <div class="srd-meta">
      <span v-if="rol.created_by"><strong>Creado por:</strong> {{ rol.created_by }}</span>
      <span v-if="rol.submitted_at"><strong>Enviado:</strong> {{ fecha(rol.submitted_at) }}</span>
      <span v-if="rol.reviewed_by"><strong>Revisado por:</strong> {{ rol.reviewed_by }}</span>
      <span v-if="rol.reviewed_at"><strong>Fecha revisión:</strong> {{ fecha(rol.reviewed_at) }}</span>
    </div>

    <div v-if="!rol.programacion_completa" class="srd-warn">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      Programación incompleta: falta actividad o turno en algún empleado.
    </div>

    <div v-for="emp in rol.empleados" :key="emp.id" class="srd-emp">
      <div class="srd-emp-name">{{ emp.empleado_nombre || 'Empleado' }} <span class="srd-dni">DNI {{ emp.dni || '—' }}</span></div>
      <div v-if="!emp.actividades.length" class="srd-empty">Sin actividades</div>
      <div v-for="act in emp.actividades" :key="act.id" class="srd-act">
        <div class="srd-act-name">
          <UIcon name="i-heroicons-bolt" class="w-3.5 h-3.5" style="color: var(--orange)" />
          {{ act.actividad_nombre || 'Actividad' }}
          <span v-if="act.requiere_consultorio" class="badge badge--neutral">Requiere consultorio</span>
        </div>
        <div v-if="!act.turnos.length" class="srd-empty">Sin turnos</div>
        <div v-for="t in act.turnos" :key="t.id" class="srd-turno">
          <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" style="color: var(--purple)" />
          <span>{{ t.horario_nombre || 'Sin horario' }}</span>
          <span v-if="t.hora_inicio" class="srd-hora">{{ t.hora_inicio }}<span v-if="t.hora_fin"> - {{ t.hora_fin }}</span></span>
          <span class="srd-dias">{{ diasLabel(t.dias_semana) }}</span>
        </div>
      </div>
    </div>
    <div v-if="!rol.empleados.length" class="srd-empty">Este rol no tiene personal.</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ rol: any }>()
const { modalidadLabel, periodoLabel, diasLabel } = useRolesTurno()
const fecha = (s: string) => s ? new Date(s).toLocaleString('es-PE', { dateStyle: 'medium', timeStyle: 'short' }) : '—'
</script>

<style scoped>
.srd-header { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.75rem; padding: 1rem; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); }
.srd-k { display: block; font-size: 0.68rem; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.04em; }
.srd-v { display: block; font-size: 0.9rem; font-weight: 700; color: var(--ink); }
.srd-meta { display: flex; flex-wrap: wrap; gap: 1rem; margin: 0.75rem 0; font-size: 0.75rem; color: var(--ink-soft); }
.srd-warn { display: flex; gap: 0.5rem; align-items: center; padding: 0.6rem 0.9rem; background: var(--amber-soft); color: var(--amber); border-radius: var(--radius); font-size: 0.8rem; margin-bottom: 0.75rem; }
.srd-emp { border: 1px solid var(--line); border-radius: var(--radius); padding: 0.85rem; margin-bottom: 0.6rem; background: var(--paper); }
.srd-emp-name { font-weight: 700; color: var(--ink); margin-bottom: 0.5rem; }
.srd-dni { font-weight: 400; font-size: 0.72rem; color: var(--ink-soft); font-family: monospace; }
.srd-act { background: var(--mist); border-radius: 6px; padding: 0.6rem; margin-bottom: 0.4rem; }
.srd-act-name { display: flex; align-items: center; gap: 0.4rem; font-weight: 600; font-size: 0.82rem; margin-bottom: 0.35rem; }
.srd-turno { display: flex; align-items: center; gap: 0.5rem; font-size: 0.78rem; padding: 0.25rem 0.4rem; background: var(--paper); border: 1px solid var(--line); border-radius: 5px; margin-bottom: 0.25rem; }
.srd-hora { font-family: monospace; color: var(--ink-soft); font-size: 0.72rem; }
.srd-dias { color: var(--ink-soft); font-size: 0.72rem; }
.srd-empty { font-size: 0.78rem; color: var(--ink-soft); padding: 0.25rem 0; }
</style>
