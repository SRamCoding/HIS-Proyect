<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <UIcon name="i-heroicons-user-circle" class="w-3.5 h-3.5" />
          <span style="color: var(--ink)">Mi Perfil</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-user-circle" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">Mi Perfil</h1>
            <p class="page-subtitle">Actualiza tus datos de acceso al panel hospitalario</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>

      <div v-if="saveSuccess" class="form-card" style="padding: 0.875rem 1.25rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.625rem; background: var(--green-soft); border-color: var(--green);">
        <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        <span style="color: var(--green); font-size: 0.875rem; font-weight: 500;">{{ saveSuccess }}</span>
      </div>

      <template v-if="!loading">
        <!-- Ficha profesional (solo lectura, si la cuenta está vinculada a un empleado) -->
        <SFormCard
          v-if="empleado"
          title="Ficha profesional"
          subtitle="Datos de tu registro en Recursos Humanos"
          icon="i-heroicons-academic-cap"
          icon-bg="var(--navy-soft)"
          icon-color="var(--navy)"
        >
          <div class="form-group">
            <label class="form-label">Nombre completo</label>
            <p class="readonly-value">{{ empleado.nombre_completo }}</p>
          </div>
          <div class="form-group">
            <label class="form-label">DNI</label>
            <p class="readonly-value font-mono-data">{{ empleado.dni }}</p>
          </div>
          <div class="form-group">
            <label class="form-label">Cargo</label>
            <p class="readonly-value">{{ empleado.cargo_laboral || '—' }}</p>
          </div>
          <div class="form-group">
            <label class="form-label">Profesión</label>
            <p class="readonly-value">{{ empleado.profesion_nombre || '—' }}</p>
          </div>
          <div class="form-group" v-if="empleado.numero_cmp || empleado.numero_colegiatura">
            <label class="form-label">Colegiatura</label>
            <p class="readonly-value font-mono-data">
              {{ empleado.numero_cmp || empleado.numero_colegiatura }}
              <span class="badge" :class="empleado.habilitado_colegio ? 'badge--ok' : 'badge--neutral'" style="margin-left: 0.5rem">
                {{ empleado.habilitado_colegio ? 'Habilitado' : 'No habilitado' }}
              </span>
            </p>
          </div>
          <div class="form-group full-width" v-if="empleado.especialidades.length">
            <label class="form-label">Especialidades</label>
            <div class="flex flex-wrap gap-2 mt-1">
              <span v-for="e in empleado.especialidades" :key="e.nombre" class="badge" :class="e.validado ? 'badge--ok' : 'badge--neutral'">
                {{ e.nombre }}{{ e.numero_rne ? ` · RNE ${e.numero_rne}` : '' }}
              </span>
            </div>
          </div>
        </SFormCard>

        <SFormCard
          title="Datos de la Cuenta"
          subtitle="Nombre, correo y contraseña de acceso"
          icon="i-heroicons-identification"
          icon-bg="var(--teal-soft)"
          icon-color="var(--teal)"
          :error="saveError"
        >
          <div class="form-group full-width">
            <label class="form-label">Nombre Completo <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-user" class="input-icon" />
              <input v-model="form.name" class="input-clinical" :class="{ 'input-error': errors.name }" />
            </div>
            <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Correo Electrónico <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-envelope" class="input-icon" />
              <input v-model="form.email" type="email" class="input-clinical" :class="{ 'input-error': errors.email }" />
            </div>
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
          </div>

          <div class="form-group full-width">
            <div class="field-hint" style="margin: 0.5rem 0 1rem 0; padding-top: 0.75rem; border-top: 1px solid var(--line);">
              Cambiar contraseña (déjalo en blanco para no modificarla)
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Contraseña Actual</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-lock-closed" class="input-icon" />
              <input v-model="form.current_password" type="password" class="input-clinical" :class="{ 'input-error': errors.current_password }" />
            </div>
            <span v-if="errors.current_password" class="error-message">{{ errors.current_password }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">Nueva Contraseña</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-key" class="input-icon" />
              <input v-model="form.new_password" type="password" class="input-clinical" :class="{ 'input-error': errors.new_password }" />
            </div>
            <ul v-if="form.new_password" class="pwd-checklist">
              <li :class="{ ok: pwdChecks.length }"><UIcon :name="pwdChecks.length ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> 8+ caracteres</li>
              <li :class="{ ok: pwdChecks.lower }"><UIcon :name="pwdChecks.lower ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Minúscula</li>
              <li :class="{ ok: pwdChecks.upper }"><UIcon :name="pwdChecks.upper ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Mayúscula</li>
              <li :class="{ ok: pwdChecks.digit }"><UIcon :name="pwdChecks.digit ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Número</li>
              <li :class="{ ok: pwdChecks.special }"><UIcon :name="pwdChecks.special ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Carácter especial</li>
            </ul>
            <span v-if="errors.new_password" class="error-message">{{ errors.new_password }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">Confirmar Nueva Contraseña</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-shield-check" class="input-icon" />
              <input v-model="form.new_password_confirm" type="password" class="input-clinical" :class="{ 'input-error': errors.new_password_confirm }" />
            </div>
            <span v-if="errors.new_password_confirm" class="error-message">{{ errors.new_password_confirm }}</span>
          </div>

          <template #actions>
            <SFormActions
              :saving="saving"
              save-text="Guardar Cambios"
              saving-text="Guardando..."
              :cancel-to="`/app?tenant=${tenantId}`"
              @save="handleSave"
            />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="[
        'El correo es tu identificador de acceso al panel',
        'La contraseña actual solo se pide si vas a cambiarla',
        'La nueva contraseña debe cumplir todos los requisitos de seguridad',
      ]" />
      <SWidgetTip text="Si cambias tu contraseña, tendrás que iniciar sesión de nuevo con ella." />
    </template>
  </SFormLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const { api } = useApi()
const authStore = useAuthStore()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || authStore.user?.tenant_id || '')

const loading = ref(true)
const saving = ref(false)
const saveError = ref('')
const saveSuccess = ref('')

interface Especialidad { nombre: string; numero_rne: string | null; validado: boolean }
interface EmpleadoPerfil {
  nombre_completo: string; dni: string; cargo_laboral: string | null
  profesion_nombre: string | null; numero_cmp: string | null; numero_colegiatura: string | null
  habilitado_colegio: boolean; especialidades: Especialidad[]
}
const empleado = ref<EmpleadoPerfil | null>(null)

const form = reactive({
  name: '', email: '', current_password: '', new_password: '', new_password_confirm: '',
})

const errors = reactive({
  name: '', email: '', current_password: '', new_password: '', new_password_confirm: '',
})

const pwdChecks = computed(() => ({
  length: form.new_password.length >= 8,
  lower: /[a-z]/.test(form.new_password),
  upper: /[A-Z]/.test(form.new_password),
  digit: /\d/.test(form.new_password),
  special: /[^\w\s]/.test(form.new_password),
}))

const validar = (): boolean => {
  errors.name = !form.name ? 'El nombre es requerido' : ''
  errors.email = !form.email ? 'El correo es requerido' : ''
  errors.current_password = ''
  errors.new_password = ''
  errors.new_password_confirm = ''

  if (form.new_password || form.new_password_confirm || form.current_password) {
    if (!form.current_password) errors.current_password = 'Ingresa tu contraseña actual'
    if (!form.new_password) {
      errors.new_password = 'La nueva contraseña es requerida'
    } else if (!Object.values(pwdChecks.value).every(Boolean)) {
      errors.new_password = 'La contraseña no cumple los requisitos mínimos'
    }
    if (!form.new_password_confirm) errors.new_password_confirm = 'Confirma la nueva contraseña'
    else if (form.new_password !== form.new_password_confirm) errors.new_password_confirm = 'Las contraseñas no coinciden'
  }

  return !Object.values(errors).some(Boolean)
}

const handleSave = async () => {
  saveError.value = ''
  saveSuccess.value = ''
  if (!validar()) return

  saving.value = true
  try {
    const body: Record<string, string> = { name: form.name, email: form.email }
    if (form.new_password) {
      body.current_password = form.current_password
      body.new_password = form.new_password
    }
    const cambioPassword = !!form.new_password
    await api('/app/perfil', { method: 'PATCH', body })

    if (cambioPassword) {
      // El backend ya invalidó la sesión (session_version) al cambiar la
      // contraseña; cerrar la sesión local ya mismo evita que la interfaz
      // siga "autenticada" con un token que la próxima petición va a rechazar.
      authStore.clearSession()
      await navigateTo(tenantId.value ? `/app/login?tenant=${tenantId.value}&aviso=password_cambiada` : '/app/login?aviso=password_cambiada')
      return
    }

    form.current_password = ''
    form.new_password = ''
    form.new_password_confirm = ''
    authStore.updateUser({ name: form.name, email: form.email })
    saveSuccess.value = 'Perfil actualizado correctamente'
  } catch (e: any) {
    saveError.value = apiErr(e, 'No se pudo guardar el perfil')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const perfil = await api<{ name: string; email: string; role: string; empleado: EmpleadoPerfil | null }>('/app/perfil')
    form.name = perfil.name
    form.email = perfil.email
    empleado.value = perfil.empleado
  } catch (e: any) {
    saveError.value = apiErr(e, 'No se pudo cargar el perfil')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.readonly-value {
  margin: 0;
  padding: 0.6rem 0.75rem;
  border-radius: var(--radius, 6px);
  background: var(--mist);
  color: var(--ink);
  font-size: 0.9rem;
}
</style>
