<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/mantenimiento/usuarios?tenant=${tenantId}`" style="color: var(--ink-soft)">Usuarios</NuxtLink>
        <span>/</span><span>Editar</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Editar Usuario</h1>
    </div>

    <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>

    <template v-else>
      <div class="p-6" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Usuario (login)*</label>
              <input v-model="form.username" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Correo electronico*</label>
              <input v-model="form.email" type="email" class="input-clinical" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Perfil</label>
            <select v-model="form.perfil_id" class="input-clinical">
              <option value="">Sin perfil</option>
              <option v-for="p in perfiles" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nueva contrasena</label>
            <input v-model="form.password" type="password" class="input-clinical" placeholder="Dejar vacio para no cambiar" />
          </div>
          <div class="flex items-center gap-2">
            <input type="checkbox" v-model="form.is_active" id="activo" />
            <label for="activo" class="text-sm" style="color: var(--ink)">Activo</label>
          </div>
        </div>
        <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>
        <div class="flex gap-3 mt-6">
          <button class="btn-primary" :disabled="saving" @click="handleSave">{{ saving ? 'Guardando...' : 'Guardar cambios' }}</button>
          <NuxtLink :to="`/sigarh/mantenimiento/usuarios?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
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
const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const perfiles = ref<any[]>([])
const form = reactive({ username: '', email: '', password: '', perfil_id: '', is_active: true })
const handleSave = async () => {
  if (!form.username.trim()) { error.value = 'El usuario es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/usuarios/${id.value}`, {
      method: 'PATCH',
      body: { username: form.username, email: form.email, perfil_id: form.perfil_id || null, is_active: form.is_active, ...(form.password && { password: form.password }) }
    })
    router.push(`/sigarh/mantenimiento/usuarios?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const [data, p] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/usuarios/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/perfiles-usuario'),
    ])
    form.username = data.username
    form.email = data.email
    form.perfil_id = data.perfil_id || ''
    form.is_active = data.is_active
    perfiles.value = p
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>