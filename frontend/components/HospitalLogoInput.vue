<script setup lang="ts">
defineProps<{ modelValue: string | null; disabled?: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: string | null]; busy: [value: boolean] }>()
const fileInput = ref<HTMLInputElement | null>(null)
const reading = ref(false)
const error = ref('')
const inputId = useId()
async function selectFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  error.value = ''
  if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type) || file.size > 2 * 1024 * 1024) {
    error.value = 'Selecciona una imagen PNG, JPG o WebP de hasta 2 MB.'
    input.value = ''
    return
  }
  reading.value = true
  emit('busy', true)
  try {
    const data = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(String(reader.result))
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
    await new Promise<void>((resolve, reject) => {
      const img = new Image()
      img.onload = () => img.naturalWidth * img.naturalHeight <= 16_000_000 ? resolve() : reject()
      img.onerror = reject
      img.src = data
    })
    emit('update:modelValue', data)
  } catch {
    error.value = 'No se pudo leer la imagen. Prueba con otro archivo de hasta 16 megapíxeles.'
  } finally {
    reading.value = false
    emit('busy', false)
    input.value = ''
  }
}
</script>
<template>
  <div class="hospital-logo-input">
    <div class="logo-preview">
      <img v-if="modelValue" :src="modelValue" alt="Vista previa del logo del hospital" />
      <UIcon v-else name="i-heroicons-building-office-2" aria-hidden="true" />
    </div>
    <div class="logo-controls">
      <label :for="inputId">Logo del hospital <span>Opcional</span></label>
      <p>Se mostrará en los accesos de App y SIGARH y en la historia clínica en PDF.</p>
      <input :id="inputId" ref="fileInput" class="sr-only" type="file" accept="image/png,image/jpeg,image/webp" :disabled="disabled || reading" @change="selectFile" />
      <div class="logo-actions">
        <button type="button" class="btn-secondary" :disabled="disabled || reading" @click="fileInput?.click()">
          <UIcon :name="reading ? 'i-heroicons-arrow-path' : 'i-heroicons-arrow-up-tray'" aria-hidden="true" />
          {{ reading ? 'Leyendo imagen…' : modelValue ? 'Cambiar logo' : 'Subir logo' }}
        </button>
        <button v-if="modelValue" type="button" class="logo-remove" :disabled="disabled || reading" @click="emit('update:modelValue', null); error = ''">Quitar</button>
      </div>
      <small>PNG, JPG o WebP · Hasta 2 MB. Se conserva la proporción de la imagen.</small>
      <p v-if="error" class="logo-error" role="alert">{{ error }}</p>
    </div>
  </div>
</template>
<style scoped>
.hospital-logo-input { display:flex; align-items:center; gap:22px; padding:22px; border:1px dashed var(--line,#e6e3ef); border-radius:16px; background:var(--mist,#f7f7fb); }
.logo-preview { display:grid; place-items:center; flex:none; width:100px; height:100px; padding:12px; border:1px solid var(--line,#e6e3ef); border-radius:18px; background:white; color:var(--teal,#7356b8); }
.logo-preview img { max-width:100%; max-height:100%; object-fit:contain; }
.logo-preview > span { width:34px; height:34px; }
.logo-controls { min-width:0; }
.logo-controls label { display:block; color:var(--ink); font-size:13px; font-weight:500; }
.logo-controls label span { margin-left:8px; color:var(--ink-soft); font-size:11px; font-weight:400; }
.logo-controls p,.logo-controls small { display:block; color:var(--ink-soft); font-size:12px; line-height:1.7; }
.logo-controls p { margin:5px 0 12px; }
.logo-controls small { margin-top:9px; font-size:11px; }
.logo-actions { display:flex; gap:16px; align-items:center; }
.logo-actions button { font-family:inherit; cursor:pointer; }
.logo-actions button:disabled { opacity:.5; cursor:wait; }
.logo-actions .btn-secondary { display:inline-flex; align-items:center; gap:8px; padding:9px 13px; background:white; border:1px solid var(--line); font-size:12px; }
.logo-remove { color:#a34343; background:none; border:0; font-size:12px; }
.logo-controls .logo-error { color:#a34343; margin-bottom:0; }
@media(max-width:560px) { .hospital-logo-input { align-items:flex-start; flex-direction:column; padding:18px; gap:14px; } }
</style>
