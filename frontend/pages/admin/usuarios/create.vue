<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="listPath" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
            <UIcon name="i-heroicons-users" class="w-3.5 h-3.5" />
            {{ isAdminView ? 'Administradores' : 'Usuarios por Hospital' }}
          </NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Nuevo Usuario</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" :style="{ background: isAdminView ? 'var(--navy-soft)' : 'var(--teal-soft)' }">
            <UIcon name="i-heroicons-user-plus" class="w-6 h-6" :style="{ color: isAdminView ? 'var(--navy)' : 'var(--teal)' }" />
          </div>
          <div>
            <h1 class="page-title">Crear Nuevo Usuario</h1>
            <p class="page-subtitle">{{ isAdminView ? 'Administradores del panel ERP' : 'Usuarios para hospitales' }}</p>
          </div>
        </div>
      </div>

      <SFormCard
        title="Datos del Usuario"
        subtitle="Completa la información para crear la cuenta"
        icon="i-heroicons-identification"
        icon-bg="var(--teal-soft)"
        icon-color="var(--teal)"
        :error="createError"
      >
        <div class="form-group full-width">
          <label class="form-label">Nombre Completo <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-user" class="input-icon" />
            <input v-model="form.name" class="input-clinical" placeholder="Ej: Juan Pérez" :class="{ 'input-error': errors.name }" />
          </div>
          <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
        </div>

        <div class="form-group full-width">
          <label class="form-label">Correo Electrónico <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-envelope" class="input-icon" />
            <input v-model="form.email" type="email" class="input-clinical" placeholder="usuario@hospital.pe" :class="{ 'input-error': errors.email }" />
          </div>
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">Contraseña <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-key" class="input-icon" />
            <input v-model="form.password" type="password" class="input-clinical" placeholder="Mínimo 8 caracteres" :class="{ 'input-error': errors.password }" />
          </div>
          <ul v-if="form.password" class="pwd-checklist">
            <li :class="{ ok: pwdChecks.length }"><UIcon :name="pwdChecks.length ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> 8+ caracteres</li>
            <li :class="{ ok: pwdChecks.lower }"><UIcon :name="pwdChecks.lower ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Minúscula</li>
            <li :class="{ ok: pwdChecks.upper }"><UIcon :name="pwdChecks.upper ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Mayúscula</li>
            <li :class="{ ok: pwdChecks.digit }"><UIcon :name="pwdChecks.digit ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Número</li>
            <li :class="{ ok: pwdChecks.special }"><UIcon :name="pwdChecks.special ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Carácter especial</li>
          </ul>
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">Confirmar Contraseña <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-shield-check" class="input-icon" />
            <input v-model="form.password_confirm" type="password" class="input-clinical" placeholder="Confirmar contraseña" :class="{ 'input-error': errors.password_confirm }" />
          </div>
          <span v-if="errors.password_confirm" class="error-message">{{ errors.password_confirm }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">Rol <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-briefcase" class="input-icon" />
            <select v-model="form.role" class="input-clinical" :class="{ 'input-error': errors.role }">
              <option value="administrador">Administrativo</option>
              <option value="medico">Médico</option>
              <option value="enfermera">Enfermera</option>
              <option value="farmaceutico">Farmacéutico</option>
              <option value="laboratorista">Laboratorista</option>
              <option value="cajero">Cajero</option>
              <option value="tuasis">TUASIS</option>
              <option value="sigarh">SIGARH</option>
            </select>
          </div>
          <span v-if="errors.role" class="error-message">{{ errors.role }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">Panel <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-squares-2x2" class="input-icon" />
            <input class="input-clinical" disabled :value="isAdminView ? 'Admin ERP' : 'Panel Hospitalario'" />
          </div>
          <span class="field-hint" v-if="!isAdminView">Las cuentas de SIGARH se crean desde SIGARH → Mantenimiento → Usuarios, donde se les asigna su perfil y rol.</span>
        </div>

        <div v-if="!isAdminView" class="form-group">
          <label class="form-label">Hospital</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-building-office-2" class="input-icon" />
            <select v-model="form.tenant_id" class="input-clinical">
              <option value="">Sin hospital</option>
              <option v-for="h in hospitales" :key="h.id" :value="h.id">{{ h.name }}</option>
            </select>
          </div>
        </div>

        <div class="form-group full-width">
          <div class="status-toggle">
            <span class="toggle-label">Usuario Activo</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
              <span class="toggle-slider" />
            </button>
          </div>
        </div>

        <template #actions>
          <SFormActions
            :saving="creating"
            save-text="Crear Usuario"
            saving-text="Creando..."
            :cancel-to="listPath"
            @save="handleCreate"
          />
        </template>
      </SFormCard>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="[
        'El correo se usa como identificador de acceso',
        'El panel define a qué interfaz podrá entrar el usuario',
        'La contraseña debe cumplir todos los requisitos de seguridad',
        'Puedes editar estos datos más adelante',
      ]" />

      <SWidgetTip text="Un usuario del panel Admin siempre debe tener el rol Administrativo." />
    </template>
  </SFormLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Hospital {
  id: string
  name: string
  domain: string
}

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const isAdminView = computed(() => route.query.tipo === 'admin')
const listPath = computed(() => isAdminView.value ? '/admin/usuarios?tipo=admin' : '/admin/usuarios')

const hospitales = ref<Hospital[]>([])
const creating = ref(false)
const createError = ref('')

const form = reactive({
  name: '',
  email: '',
  password: '',
  password_confirm: '',
  role: 'administrador',
  panel: isAdminView.value ? 'admin' : 'app',
  tenant_id: '',
  is_active: true,
})

const errors = reactive({
  name: '',
  email: '',
  password: '',
  password_confirm: '',
  role: '',
})

const pwdChecks = computed(() => ({
  length: form.password.length >= 8,
  lower: /[a-z]/.test(form.password),
  upper: /[A-Z]/.test(form.password),
  digit: /\d/.test(form.password),
  special: /[^\w\s]/.test(form.password),
}))

const validateForm = (): boolean => {
  errors.name = !form.name ? 'El nombre es requerido' : ''
  errors.email = !form.email ? 'El correo es requerido' : ''
  errors.password = !form.password
    ? 'La contraseña es requerida'
    : (!Object.values(pwdChecks.value).every(Boolean) ? 'La contraseña no cumple los requisitos mínimos' : '')
  errors.password_confirm = form.password && form.password !== form.password_confirm ? 'Las contraseñas no coinciden' : ''
  errors.role = !form.role ? 'El rol es requerido' : ''

  return !(errors.name || errors.email || errors.password || errors.password_confirm || errors.role)
}

const handleCreate = async () => {
  if (!validateForm()) return

  creating.value = true
  createError.value = ''
  try {
    const body: any = {
      name: form.name,
      email: form.email,
      password: form.password,
      role: form.role,
      panel: isAdminView.value ? 'admin' : form.panel,
      tenant_id: form.tenant_id || null,
      is_active: form.is_active,
    }

    await api('/admin/usuarios', { method: 'POST', body })
    router.push(listPath.value)
  } catch (e: any) {
    createError.value = apiErr(e, 'No se pudo crear el usuario')
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  try {
    hospitales.value = await api<Hospital[]>('/admin/hospitales')
  } catch {
    // el selector de hospital queda vacio si falla; no bloquea la creacion
  }
})
</script>
