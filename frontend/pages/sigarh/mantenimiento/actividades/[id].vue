<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/mantenimiento/actividades?tenant=${tenantId}`" style="color: var(--ink-soft)">Actividades</NuxtLink>
        <span>/</span><span>Editar</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Editar Actividad</h1>
    </div>

    <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>

    <template v-else>
      <div class="p-6" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nombre*</label>
            <input v-model="form.nombre" class="input-clinical" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Codigo</label>
            <input v-model="form.codigo" class="input-clinical" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Tipo de Actividad</label>
            <select v-model="form.tipo_actividad_id" class="input-clinical">
              <option value="">Sin tipo</option>
              <option v-for="t in tiposActividad" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <input type="checkbox" v-model="form.is_active" id="activo" />
            <label for="activo" class="text-sm" style="color: var(--ink)">Activo</label>
          </div>
        </div>
        <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>
        <div class="flex gap-3 mt-6">
          <button class="btn-primary" :disabled="saving" @click="handleSave">{{ saving ? 'Guardando...' : 'Guardar cambios' }}</button>
          <NuxtLink :to="`/sigarh/mantenimiento/actividades?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId =