<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const route = useRoute()
const router = useRouter()
const { categoriaLabel, categoriaValida, tiposDe, tipoLabel } = useRolesTurno()
const tenantId = computed(() => route.query.tenant as string || '')
const categoria = computed(() => route.params.categoria as string)

onMounted(() => {
  if (!categoriaValida(categoria.value)) return
  const tipos = tiposDe(categoria.value)
  // Si la categoria tiene una sola modalidad, entra directo.
  if (tipos.length === 1) {
    router.replace(`/sigarh/creacion-roles/${categoria.value}/${tipos[0]}?tenant=${tenantId.value}`)
  }
})
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <h1 class="page-title">Creación de Roles</h1>
          <p class="page-subtitle">{{ categoriaValida(categoria) ? categoriaLabel(categoria) : 'Categoría no válida' }}</p>
        </div>
      </div>
    </div>

    <div v-if="!categoriaValida(categoria)" class="sigarh-table-state">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
      <p style="color: var(--alert)">La categoría "{{ categoria }}" no existe.</p>
    </div>

    <div v-else class="modalidades-grid">
      <NuxtLink
        v-for="t in tiposDe(categoria)"
        :key="t"
        :to="`/sigarh/creacion-roles/${categoria}/${t}?tenant=${tenantId}`"
        class="modalidad-card"
      >
        <div class="modalidad-icon"><UIcon name="i-heroicons-document-plus" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div>
          <div class="modalidad-title">{{ tipoLabel(t) }}</div>
          <div class="modalidad-sub">Ver y crear roles de esta modalidad</div>
        </div>
        <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" style="color: var(--ink-soft)" />
      </NuxtLink>
    </div>
  </div>
</template>

<style scoped>
.modalidades-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 0.75rem; }
.modalidad-card { display: flex; align-items: center; gap: 0.85rem; padding: 1rem 1.1rem; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); text-decoration: none; transition: all .15s ease; }
.modalidad-card:hover { border-color: var(--navy-soft); transform: translateY(-1px); }
.modalidad-icon { width: 40px; height: 40px; border-radius: 11px; background: var(--navy-soft); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.modalidad-title { font-size: 0.9rem; font-weight: 600; color: var(--ink); }
.modalidad-sub { font-size: 0.75rem; color: var(--ink-soft); }
.modalidad-card > div:nth-child(2) { flex: 1; }
</style>
