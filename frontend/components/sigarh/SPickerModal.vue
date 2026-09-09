<template>
  <SModal
    :model-value="modelValue"
    :title="title"
    :subtitle="subtitle"
    :icon="icon"
    :icon-bg="iconBg"
    :icon-color="iconColor"
    width="560px"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="$emit('update:modelValue', false)"
  >
    <div class="pk-search">
      <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" style="color: var(--ink-soft)" />
      <input ref="searchEl" v-model="q" type="text" :placeholder="searchPlaceholder" />
      <button v-if="q" @click="q = ''"><UIcon name="i-heroicons-x-mark" class="w-3.5 h-3.5" /></button>
    </div>

    <div class="pk-bar">
      <span>{{ seleccion.length }} seleccionado(s)</span>
      <button v-if="multiple && filtrados.length" @click="toggleTodos">
        {{ todosSel ? 'Quitar todos' : 'Seleccionar todos' }}
      </button>
    </div>

    <div class="pk-list">
      <p v-if="!filtrados.length" class="pk-empty">{{ emptyText }}</p>
      <label v-for="it in filtrados" :key="it.id" class="pk-item" :class="{ on: seleccion.includes(it.id) }">
        <input
          :type="multiple ? 'checkbox' : 'radio'"
          :checked="seleccion.includes(it.id)"
          @change="pick(it.id)"
        />
        <span class="pk-item-main">
          <span class="pk-item-label">{{ it.label }}</span>
          <span v-if="it.sublabel" class="pk-item-sub">{{ it.sublabel }}</span>
        </span>
        <span v-if="it.badge" class="badge badge--neutral">{{ it.badge }}</span>
      </label>
    </div>

    <template #footer>
      <button class="btn-cancel" @click="$emit('update:modelValue', false)">Cancelar</button>
      <button class="btn-primary" :disabled="!seleccion.length" @click="confirmar">
        {{ confirmText }}<span v-if="multiple && seleccion.length"> ({{ seleccion.length }})</span>
      </button>
    </template>
  </SModal>
</template>

<script setup lang="ts">
interface Opcion { id: string; label: string; sublabel?: string; badge?: string }
const props = withDefaults(defineProps<{
  modelValue: boolean
  title: string
  subtitle?: string
  items: Opcion[]
  multiple?: boolean
  icon?: string
  iconBg?: string
  iconColor?: string
  searchPlaceholder?: string
  emptyText?: string
  confirmText?: string
}>(), {
  multiple: true,
  icon: 'i-heroicons-user-plus',
  searchPlaceholder: 'Buscar...',
  emptyText: 'Sin resultados',
  confirmText: 'Agregar',
})
const emit = defineEmits(['update:modelValue', 'confirm'])

const q = ref('')
const seleccion = ref<string[]>([])
const searchEl = ref<HTMLInputElement>()

watch(() => props.modelValue, (v) => {
  if (v) { seleccion.value = []; q.value = ''; nextTick(() => searchEl.value?.focus()) }
})

const filtrados = computed(() => {
  const s = q.value.trim().toLowerCase()
  if (!s) return props.items
  return props.items.filter(i =>
    i.label.toLowerCase().includes(s) || (i.sublabel || '').toLowerCase().includes(s))
})
const todosSel = computed(() => filtrados.value.length > 0 && filtrados.value.every(i => seleccion.value.includes(i.id)))

const pick = (id: string) => {
  if (props.multiple) {
    seleccion.value = seleccion.value.includes(id)
      ? seleccion.value.filter(x => x !== id)
      : [...seleccion.value, id]
  } else {
    seleccion.value = [id]
  }
}
const toggleTodos = () => {
  seleccion.value = todosSel.value
    ? seleccion.value.filter(id => !filtrados.value.some(i => i.id === id))
    : [...new Set([...seleccion.value, ...filtrados.value.map(i => i.id)])]
}
const confirmar = () => {
  emit('confirm', props.multiple ? [...seleccion.value] : seleccion.value[0])
  emit('update:modelValue', false)
}
</script>

<style scoped>
.pk-search {
  display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.75rem;
  border: 1px solid var(--line); border-radius: 8px; margin-bottom: 0.75rem;
}
.pk-search input { flex: 1; border: none; outline: none; font-size: 0.875rem; background: transparent; color: var(--ink); }
.pk-search button { background: none; border: none; cursor: pointer; color: var(--ink-soft); display: flex; }
.pk-bar { display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: var(--ink-soft); margin-bottom: 0.4rem; }
.pk-bar button { background: none; border: none; color: var(--teal); font-weight: 600; font-size: 0.75rem; cursor: pointer; }
.pk-bar button:hover { text-decoration: underline; }
.pk-list { max-height: 44vh; overflow-y: auto; border: 1px solid var(--line); border-radius: 8px; }
.pk-empty { padding: 1.5rem; text-align: center; font-size: 0.8125rem; color: var(--ink-soft); margin: 0; }
.pk-item {
  display: flex; align-items: center; gap: 0.6rem; padding: 0.6rem 0.75rem;
  border-bottom: 1px solid var(--line); cursor: pointer; transition: background .12s ease;
}
.pk-item:last-child { border-bottom: none; }
.pk-item:hover { background: var(--mist); }
.pk-item.on { background: var(--teal-soft); }
.pk-item input { width: 15px; height: 15px; accent-color: var(--teal); cursor: pointer; flex-shrink: 0; }
.pk-item-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.pk-item-label { font-size: 0.85rem; color: var(--ink); font-weight: 500; }
.pk-item-sub { font-size: 0.72rem; color: var(--ink-soft); font-family: monospace; }
</style>
