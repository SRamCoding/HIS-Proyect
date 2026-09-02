<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId}`" style="color: var(--ink-soft)">Perfiles de Usuario</NuxtLink>
        <span>/</span><span>Crear</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Nuevo Perfil de Usuario</h1>
    </div>

    <div class="p-6" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nombre*</label>
          <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Administrador" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Rol del Sistema</label>
          <select v-model="form.rol_sistema_id" class="input-clinical">
            <option value="">Sin rol</option>
            <option v-for="r in rolesSistema" :key="r.id" :value="r.id">{{ r.nombre }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Descripcion</label>
          <textarea v-model="form.descripcion" class="input-clinical" rows="2" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2" style="color: var(--ink)">Modulos con acceso</label>
          <div class="grid grid-cols-2 gap-2 p-3 rounded" style="border: 1px solid var(--line)">
            <label v-for="mod in todosModulos" :key="mod" class="flex items-center gap-2 text-sm cursor-pointer" style="color: var(--ink)">
              <input type="checkbox" :value="mod" v-model="form.modulos_acceso" />
              {{ formatModulo(mod) }}
            </label>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <input type="checkbox" v-model="form.is_active" id="activo" />
          <label for="activo" class="text-sm" style="color: var(--ink)">Activo</label>
        </div>
      </div>
      <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>
      <div class="flex gap-3 mt-6">
        <button class="btn-primary" :disabled="saving" @click="handleCreate(false)">{{ saving ? 'Guardando...' : 'Crear' }}</button>
        <button class="px-4 py-2 rounded text-sm font-medium" style="border: 1px solid var(--line); color: var(--ink)" :disabled="saving" @click="handleCreate(true)">Crear y crear otro</button>
        <NuxtLink :to="`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const rolesSistema = ref<any[]>([])
const authStore = useAuthStore()

const todosModulos = computed(() => authStore.user?.active_modules?.filter(m => m.startsWith('sigarh_')) || [])
const formatModulo = (code: string) => code.replace('sigarh_', '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

const form = reactive({ nombre: '', rol_sistema_id: '', descripcion: '', modulos_acceso: [] as string[], is_active: true })

const handleCreate = async (createAnother: boolean) => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/perfiles-usuario', {
      method: 'POST',
      body: { ...form, rol_sistema_id: form.rol_sistema_id || null }
    })
    if (createAnother) { Object.assign(form, { nombre: '', rol_sistema_id: '', descripcion: '', modulos_acceso: [], is_active: true }) }
    else { router.push(`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId.value}`) }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear' }
  finally { saving.value = false }
}

onMounted(async () => {
  rolesSistema.value = await api<any[]>('/sigarh/mantenimiento/roles-sistema')
})
</script>