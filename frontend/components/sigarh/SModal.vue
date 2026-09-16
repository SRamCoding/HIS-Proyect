<template>
  <Teleport to="body">
    <Transition name="s-modal">
      <div v-if="modelValue" class="s-modal-overlay" @click.self="close">
        <div ref="modalEl" class="s-modal" :style="{ maxWidth: width }" role="dialog" aria-modal="true" :aria-labelledby="titleId" tabindex="-1" @keydown.tab="onTabKey">
          <div class="s-modal-head">
            <div class="s-modal-title">
              <div v-if="icon" class="s-modal-icon" :style="{ background: iconBg }">
                <UIcon :name="icon" class="w-4 h-4" :style="{ color: iconColor }" />
              </div>
              <div>
                <h3 :id="titleId">{{ title }}</h3>
                <p v-if="subtitle">{{ subtitle }}</p>
              </div>
            </div>
            <button class="s-modal-x" @click="close" aria-label="Cerrar"><UIcon name="i-heroicons-x-mark" class="w-5 h-5" /></button>
          </div>

          <div class="s-modal-body"><slot /></div>

          <div v-if="$slots.footer" class="s-modal-foot"><slot name="footer" /></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: boolean
  title: string
  subtitle?: string
  icon?: string
  iconBg?: string
  iconColor?: string
  width?: string
  persistent?: boolean
}>(), {
  iconBg: 'var(--navy-soft)',
  iconColor: 'var(--navy)',
  width: '520px',
})
const emit = defineEmits(['update:modelValue', 'close'])
const close = () => { if (props.persistent) return; emit('update:modelValue', false); emit('close') }

const titleId = `s-modal-title-${Math.random().toString(36).slice(2, 10)}`
const modalEl = ref<HTMLElement | null>(null)
let elementoPrevio: HTMLElement | null = null

const focoteables = () =>
  modalEl.value
    ? Array.from(modalEl.value.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )).filter(el => el.offsetParent !== null)
    : []

// Trampa de foco: Tab/Shift+Tab deben ciclar dentro del modal, nunca escapar
// hacia el contenido de atras -- sin esto, con el mouse quieto y solo
// teclado, alguien podia tabular fuera del dialogo hacia botones tapados
// visualmente por el overlay pero todavia montados y alcanzables.
const onTabKey = (e: KeyboardEvent) => {
  const elementos = focoteables()
  if (!elementos.length) { e.preventDefault(); return }
  const primero = elementos[0]
  const ultimo = elementos[elementos.length - 1]
  if (e.shiftKey && document.activeElement === primero) {
    e.preventDefault(); ultimo.focus()
  } else if (!e.shiftKey && document.activeElement === ultimo) {
    e.preventDefault(); primero.focus()
  }
}

const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') close() }
watch(() => props.modelValue, async (v) => {
  if (!import.meta.client) return
  document.body.style.overflow = v ? 'hidden' : ''
  if (v) {
    window.addEventListener('keydown', onKey)
    elementoPrevio = document.activeElement as HTMLElement | null
    await nextTick()
    // Mueve el foco AL modal apenas abre -- si nadie hace nada, el foco del
    // teclado se queda en lo que estaba antes (a menudo el boton que abrio
    // el modal, ya tapado detras del overlay).
    const elementos = focoteables()
    ;(elementos[0] ?? modalEl.value)?.focus()
  } else {
    window.removeEventListener('keydown', onKey)
    elementoPrevio?.focus()
    elementoPrevio = null
  }
})
onUnmounted(() => { if (import.meta.client) { document.body.style.overflow = ''; window.removeEventListener('keydown', onKey) } })
</script>

<style scoped>
.s-modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(16, 28, 36, 0.45); backdrop-filter: blur(3px);
  display: flex; align-items: flex-start; justify-content: center;
  padding: 6vh 1rem 1rem;
}
.s-modal {
  width: 100%; background: var(--paper); border-radius: var(--radius-lg);
  box-shadow: 0 24px 60px rgba(15, 31, 46, 0.28); display: flex; flex-direction: column;
  max-height: 84vh; overflow: hidden;
}
.s-modal-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.25rem; border-bottom: 1px solid var(--line);
}
.s-modal-title { display: flex; align-items: center; gap: 0.75rem; }
.s-modal-icon { width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.s-modal-title h3 { margin: 0; font-size: 0.95rem; font-weight: 700; color: var(--ink); }
.s-modal-title p { margin: 0.1rem 0 0; font-size: 0.75rem; color: var(--ink-soft); }
.s-modal-x { background: none; border: none; cursor: pointer; color: var(--ink-soft); padding: 0.25rem; border-radius: 8px; display: flex; }
.s-modal-x:hover { background: var(--mist); color: var(--ink); }
.s-modal-body { padding: 1.1rem 1.25rem; overflow-y: auto; }
.s-modal-foot { padding: 0.85rem 1.25rem; border-top: 1px solid var(--line); display: flex; justify-content: flex-end; gap: 0.5rem; background: var(--mist); }

.s-modal-enter-active, .s-modal-leave-active { transition: opacity .18s ease; }
.s-modal-enter-active .s-modal, .s-modal-leave-active .s-modal { transition: transform .2s ease, opacity .2s ease; }
.s-modal-enter-from, .s-modal-leave-to { opacity: 0; }
.s-modal-enter-from .s-modal, .s-modal-leave-to .s-modal { transform: translateY(-12px); opacity: 0; }
</style>
