<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink to="/admin/hospitales" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
            <UIcon name="i-heroicons-building-office-2" class="w-3.5 h-3.5" />
            Hospitales
          </NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Reintentar aprovisionamiento</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--amber-soft)">
            <UIcon name="i-heroicons-arrow-path" class="w-6 h-6" style="color: var(--amber)" />
          </div>
          <div>
            <h1 class="page-title">Reintentar aprovisionamiento</h1>
            <p class="page-subtitle">{{ hospital?.name || 'Cargando...' }}</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>

      <div v-else-if="hospital && hospital.provisioning_status !== 'error'" class="form-card" style="padding: 1.5rem; text-align: center">
        <UIcon name="i-heroicons-check-circle" class="w-8 h-8" style="color: var(--green, #16a34a)" />
        <p style="margin-top: 0.75rem; color: var(--ink)">Este hospital ya no está en estado de error.</p>
        <NuxtLink to="/admin/hospitales" class="btn-outline" style="margin-top: 1rem; display: inline-flex">Volver al listado</NuxtLink>
      </div>

      <template v-else-if="hospital">
        <div class="form-card" style="padding: 0.875rem 1.25rem; margin-bottom: 1rem; display: flex; align-items: flex-start; gap: 0.625rem; background: var(--alert-soft); border-color: var(--alert);">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 shrink-0" style="color: var(--alert); margin-top: 0.1rem" />
          <div>
            <p style="color: var(--alert); font-size: 0.875rem; font-weight: 600; margin: 0">El aprovisionamiento anterior falló</p>
            <p v-if="hospital.provisioning_error" style="color: var(--alert); font-size: 0.8125rem; margin: 0.25rem 0 0 0">{{ hospital.provisioning_error }}</p>
          </div>
        </div>

        <div class="form-card" style="padding: 0.875rem 1.25rem; margin-bottom: 1rem; display: flex; align-items: flex-start; gap: 0.625rem;">
          <UIcon name="i-heroicons-information-circle" class="w-5 h-5 shrink-0" style="color: var(--ink-soft); margin-top: 0.1rem" />
          <p style="color: var(--ink-soft); font-size: 0.8125rem; margin: 0">
            Las contraseñas no se guardan en ningún lado tras un intento fallido, así que hay que ingresarlas de nuevo.
            Pueden ser las mismas u otras distintas — quedarán como las credenciales iniciales de este hospital.
          </p>
        </div>

        <SFormCard
          title="Usuario App"
          subtitle="Administrador del panel hospitalario (App)"
          icon="i-heroicons-user-circle"
          icon-bg="var(--navy-soft)"
          icon-color="var(--navy)"
        >
          <div class="form-group full-width">
            <label class="form-label">Nombre Completo <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-user" class="input-icon" />
              <input v-model="form.admin_name" class="input-clinical" :class="{ 'input-error': errors.admin_name }" />
            </div>
            <span v-if="errors.admin_name" class="error-message">{{ errors.admin_name }}</span>
          </div>
          <div class="form-group full-width">
            <label class="form-label">Correo Electrónico <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-envelope" class="input-icon" />
              <input v-model="form.admin_email" type="email" class="input-clinical" :class="{ 'input-error': errors.admin_email }" />
            </div>
            <span v-if="errors.admin_email" class="error-message">{{ errors.admin_email }}</span>
          </div>
          <div class="form-group full-width">
            <label class="form-label">Contraseña <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-lock-closed" class="input-icon" />
              <input v-model="form.admin_password" type="password" class="input-clinical" :class="{ 'input-error': errors.admin_password }" />
            </div>
            <ul class="pwd-checklist">
              <li :class="{ ok: adminPwdChecks.length }"><UIcon :name="adminPwdChecks.length ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> 8+ caracteres</li>
              <li :class="{ ok: adminPwdChecks.lower }"><UIcon :name="adminPwdChecks.lower ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Minúscula</li>
              <li :class="{ ok: adminPwdChecks.upper }"><UIcon :name="adminPwdChecks.upper ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Mayúscula</li>
              <li :class="{ ok: adminPwdChecks.digit }"><UIcon :name="adminPwdChecks.digit ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Número</li>
              <li :class="{ ok: adminPwdChecks.special }"><UIcon :name="adminPwdChecks.special ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Carácter especial</li>
            </ul>
            <span v-if="errors.admin_password" class="error-message">{{ errors.admin_password }}</span>
          </div>
        </SFormCard>

        <SFormCard
          title="Usuario SIGARH"
          subtitle="Administrador del panel SIGARH"
          icon="i-heroicons-folder-open"
          icon-bg="var(--purple-soft)"
          icon-color="var(--purple)"
          :error="saveError"
        >
          <div class="form-group full-width">
            <label class="form-label">Nombre Completo <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-user" class="input-icon" />
              <input v-model="form.sigarh_name" class="input-clinical" :class="{ 'input-error': errors.sigarh_name }" />
            </div>
            <span v-if="errors.sigarh_name" class="error-message">{{ errors.sigarh_name }}</span>
          </div>
          <div class="form-group full-width">
            <label class="form-label">Correo Electrónico <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-envelope" class="input-icon" />
              <input v-model="form.sigarh_email" type="email" class="input-clinical" :class="{ 'input-error': errors.sigarh_email }" />
            </div>
            <span v-if="errors.sigarh_email" class="error-message">{{ errors.sigarh_email }}</span>
          </div>
          <div class="form-group full-width">
            <label class="form-label">Contraseña <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-lock-closed" class="input-icon" />
              <input v-model="form.sigarh_password" type="password" class="input-clinical" :class="{ 'input-error': errors.sigarh_password }" />
            </div>
            <ul class="pwd-checklist">
              <li :class="{ ok: sigarhPwdChecks.length }"><UIcon :name="sigarhPwdChecks.length ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> 8+ caracteres</li>
              <li :class="{ ok: sigarhPwdChecks.lower }"><UIcon :name="sigarhPwdChecks.lower ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Minúscula</li>
              <li :class="{ ok: sigarhPwdChecks.upper }"><UIcon :name="sigarhPwdChecks.upper ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Mayúscula</li>
              <li :class="{ ok: sigarhPwdChecks.digit }"><UIcon :name="sigarhPwdChecks.digit ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Número</li>
              <li :class="{ ok: sigarhPwdChecks.special }"><UIcon :name="sigarhPwdChecks.special ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Carácter especial</li>
            </ul>
            <span v-if="errors.sigarh_password" class="error-message">{{ errors.sigarh_password }}</span>
          </div>

          <template #actions>
            <SFormActions
              :saving="saving"
              save-text="Reintentar aprovisionamiento"
              saving-text="Encolando..."
              cancel-to="/admin/hospitales"
              @save="handleSave"
            />
          </template>
        </SFormCard>
      </template>

      <div v-else class="form-card" style="padding: 1.5rem; text-align: center">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="margin-top: 0.75rem; color: var(--ink)">{{ saveError || 'No se pudo cargar el hospital' }}</p>
        <NuxtLink to="/admin/hospitales" class="btn-outline" style="margin-top: 1rem; display: inline-flex">Volver al listado</NuxtLink>
      </div>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="[
        'El hospital, su nivel y sus módulos contratados no cambian: solo se reintenta crear la base física y los usuarios iniciales',
        'Las contraseñas viajan hasheadas a la cola de tareas, nunca en claro',
        'El estado pasará a Aprovisionando apenas se encole el reintento',
      ]" />
      <SWidgetTip text="Si el reintento vuelve a fallar, revisa el detalle del error mostrado arriba antes de intentar de nuevo." />
    </template>
  </SFormLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Hospital {
  id: string
  name: string
  provisioning_status: string
  provisioning_error: string | null
  admin_name: string | null
  admin_email: string | null
  sigarh_name: string | null
  sigarh_email: string | null
}

const { api } = useApi()
const route = useRoute()
const router = useRouter()
const id = computed(() => route.params.id as string)

const loading = ref(true)
const saving = ref(false)
const saveError = ref('')
const hospital = ref<Hospital | null>(null)

const form = reactive({
  admin_name: '', admin_email: '', admin_password: '',
  sigarh_name: '', sigarh_email: '', sigarh_password: '',
})

const errors = reactive({
  admin_name: '', admin_email: '', admin_password: '',
  sigarh_name: '', sigarh_email: '', sigarh_password: '',
})

const emailValido = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)

const checksDePassword = (pwd: string) => ({
  length: pwd.length >= 8,
  lower: /[a-z]/.test(pwd),
  upper: /[A-Z]/.test(pwd),
  digit: /\d/.test(pwd),
  special: /[^\w\s]/.test(pwd),
})

const adminPwdChecks = computed(() => checksDePassword(form.admin_password))
const sigarhPwdChecks = computed(() => checksDePassword(form.sigarh_password))

const validar = (): boolean => {
  errors.admin_name = !form.admin_name ? 'El nombre es requerido' : ''
  errors.admin_email = !form.admin_email ? 'El correo es requerido' : !emailValido(form.admin_email) ? 'Correo inválido' : ''
  errors.admin_password = !form.admin_password ? 'La contraseña es requerida' : !Object.values(adminPwdChecks.value).every(Boolean) ? 'No cumple los requisitos mínimos' : ''
  errors.sigarh_name = !form.sigarh_name ? 'El nombre es requerido' : ''
  errors.sigarh_email = !form.sigarh_email ? 'El correo es requerido' : !emailValido(form.sigarh_email) ? 'Correo inválido' : ''
  errors.sigarh_password = !form.sigarh_password ? 'La contraseña es requerida' : !Object.values(sigarhPwdChecks.value).every(Boolean) ? 'No cumple los requisitos mínimos' : ''

  if (!errors.admin_email && !errors.sigarh_email && form.admin_email === form.sigarh_email) {
    errors.admin_email = 'Los usuarios App y SIGARH deben usar correos diferentes'
    errors.sigarh_email = 'Los usuarios App y SIGARH deben usar correos diferentes'
  }

  return !Object.values(errors).some(Boolean)
}

const handleSave = async () => {
  saveError.value = ''
  if (!validar()) return
  saving.value = true
  try {
    await api(`/admin/hospitales/${id.value}/reintentar-aprovisionamiento`, { method: 'POST', body: { ...form } })
    router.push('/admin/hospitales')
  } catch (e: any) {
    saveError.value = apiErr(e, 'No se pudo encolar el reintento')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    hospital.value = await api<Hospital>(`/admin/hospitales/${id.value}`)
    // Nombre y correo no son datos sensibles y si se guardan entre
    // intentos -- solo la contraseña se pide siempre desde cero.
    form.admin_name = hospital.value.admin_name ?? ''
    form.admin_email = hospital.value.admin_email ?? ''
    form.sigarh_name = hospital.value.sigarh_name ?? ''
    form.sigarh_email = hospital.value.sigarh_email ?? ''
  } catch (e: any) {
    saveError.value = apiErr(e, 'No se pudo cargar el hospital')
  } finally {
    loading.value = false
  }
})
</script>
