<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/mantenimiento/usuarios?tenant=${tenantId}`" style="color: var(--ink-soft)">Usuarios</NuxtLink>
        <span>/</span><span>Crear</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Nuevo Usuario</h1>
    </div>

    <div class="p-6" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Usuario (login)*</label>
            <input v-model="form.username" class="input-clinical" placeholder="Ej: jperez" />
            <p class="text-xs mt-1" style="color: var(--ink-soft)">Se genera automaticamente con el DNI.</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Correo electronico*</label>
            <input v-model="form.email" type="email" class="input-clinical" placeholder="usuario@hospital.pe" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Perfil*</label>
          <select v-model="form.perfil_id" class="input-clinical">
            <option value="">Seleccione una opcion</option>
            <option v-for="p in perfiles" :key="p.id" :value="p.id">{{ p.nombre }}</option>
          </select>
          <p class="text-xs mt-1" style="color: var(--ink-soft)">El rol y los modulos se toman del perfil seleccionado.</p>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Contrasena</label>
          <input v-model="form.password" type="password" class="input-clinical" placeholder="Por defecto: DNI del empleado" />
          <p class="text-xs mt-1" style="color: var(--ink-soft)">Si no ingresa, se usara el DNI del empleado.</p>
        </div>
        <div class="flex items-center gap-2">
          <input type="checkbox" v-model="form.is_active" id="activo" />
          <label for="activo" class="text-sm" style="color: var(--ink)">Activo</label>
        </div>
      </div>

      <!-- Perfil asignado preview -->
      <div v-if="perfilSeleccionado" class="mt-4 p-4 rounded" style="border: 1px solid var(--line)">
        <p class="text-sm font-semibold mb-2" style="color: var(--ink)">Perfil asignado</p>
        <p class="text-xs" style="color: var(--ink-soft)">Rol del sistema: <span style="color: var(--ink)">{{ perfilSeleccionado.nombre }}</span></p>
      </div>
      <div v-else class="mt-4 p-4 rounded" style="border: 1px solid var(--line)">
        <p class="text-sm font-semibold mb-1" style="color: var(--ink)">Perfil asignado</p>
        <p class="text-xs" style="color: var(--ink-soft)">— Seleccione un perfil —</p>
      </div>

      <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>
      <div class="flex gap-3 mt-6">
        <button class="btn-primary" :disabled="saving" @click="handleCreate(false)">{{ saving ? 'Guardando...' : 'Crear' }}</button>
        <button class="px-4 py-2 rounded text-sm font-medium" style="border: 1px solid var(--line); color: var(--ink)" :disabled="saving" @click="handleCreate(true)">Crear y crear otro</button>
        <NuxtLink :to="`/sigarh/mantenimiento/usuarios?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
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
const perfiles = ref<any[]>([])
const form = reactive({ username: '', email: '', password: '', perfil_id: '', is_active: true })
const perfilSeleccionado = computed(() => perfiles.value.find(p => p.id === form.perfil_id) || null)
const handleCreate = async (createAnother: boolean) => {
  if (!form.username.trim()) { error.value = 'El usuario es requerido'; return }
  if (!form.email.trim()) { error.value = 'El correo es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/usuarios', {
      method: 'POST',
      body: { ...form, perfil_id: form.perfil_id || null, password: form.password || form.username }
    })
    if (createAnother) { Object.assign(form, { username: '', email: '', password: '', perfil_id: '', is_active: true }) }
    else { router.push(`/sigarh/mantenimiento/usuarios?tenant=${tenantId.value}`) }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear' }
  finally { saving.value = false }
}
onMounted(async () => {
  perfiles.value = await api<any[]>('/sigarh/mantenimiento/perfiles-usuario')
})
</script>