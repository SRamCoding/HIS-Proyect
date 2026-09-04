<!-- components/ui/FilterBar.vue -->
<template>
  <div class="filter-bar" :style="{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }">
    <div class="filter-left" :style="{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', flex: 1 }">
      <div class="search-wrapper" :style="{ position: 'relative', minWidth: '200px', flex: 1, maxWidth: '300px' }">
        <UIcon name="i-heroicons-magnifying-glass" class="search-icon" :style="{
          position: 'absolute',
          left: '0.75rem',
          top: '50%',
          transform: 'translateY(-50%)',
          width: '1rem',
          height: '1rem',
          color: 'var(--ink-soft)'
        }" />
        <input
          v-model="searchValue"
          type="text"
          class="search-input"
          :placeholder="searchPlaceholder || 'Buscar...'"
          :style="{
            width: '100%',
            padding: '0.5rem 0.75rem 0.5rem 2.5rem',
            borderRadius: '8px',
            fontSize: '0.875rem',
            border: '1px solid var(--line)',
            background: 'var(--paper)',
            transition: 'all 0.2s ease'
          }"
        />
      </div>

      <div class="filter-group" :style="{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap' }">
        <button
          v-for="filter in filters"
          :key="filter.value"
          class="filter-chip"
          :class="{ 'filter-chip--active': activeFilter === filter.value }"
          :style="{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.375rem',
            padding: '0.375rem 0.75rem',
            borderRadius: '20px',
            fontSize: '0.75rem',
            fontWeight: 500,
            border: '1px solid var(--line)',
            background: activeFilter === filter.value ? 'var(--teal-soft)' : 'transparent',
            color: activeFilter === filter.value ? 'var(--teal)' : 'var(--ink-soft)',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }"
          @click="$emit('update:activeFilter', filter.value)"
        >
          {{ filter.label }}
          <span class="filter-count" :style="{
            padding: '0.0625rem 0.375rem',
            borderRadius: '10px',
            fontSize: '0.625rem',
            fontWeight: 600,
            color: activeFilter === filter.value ? 'white' : 'var(--ink-soft)',
            background: activeFilter === filter.value ? 'var(--teal)' : 'var(--mist)',
            transition: 'all 0.2s ease'
          }">
            {{ filter.count }}
          </span>
        </button>
      </div>
    </div>
    <div class="filter-right" :style="{ display: 'flex', alignItems: 'center', gap: '0.75rem' }">
      <span class="result-count" style="font-size: 0.8125rem; color: var(--ink-soft)">
        {{ resultCount || `${totalCount} resultados` }}
      </span>
      <button
        v-if="showClear"
        class="btn-secondary btn-sm"
        :style="{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.375rem 0.75rem',
          borderRadius: '6px',
          fontSize: '0.75rem',
          fontWeight: 500,
          border: '1px solid var(--line)',
          background: 'var(--paper)',
          color: 'var(--ink)',
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }"
        @click="$emit('clear')"
      >
        <UIcon name="i-heroicons-arrow-path" class="w-3.5 h-3.5" />
        Resetear
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Filter {
  label: string
  value: string
  count: number
}

const props = defineProps<{
  search?: string
  searchPlaceholder?: string
  filters: Filter[]
  activeFilter?: string
  totalCount?: number
  resultCount?: string
  showClear?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:search', value: string): void
  (e: 'update:activeFilter', value: string): void
  (e: 'clear'): void
}>()

// computed en vez de ref: mantiene sincronizado el input con el estado
// del padre (ej. cuando clearFilters() hace search.value = '')
const searchValue = computed({
  get: () => props.search ?? '',
  set: (v: string) => emit('update:search', v)
})
</script>

<style scoped>
.filter-chip--active {
  background: var(--teal-soft) !important;
  border-color: var(--teal) !important;
  color: var(--teal) !important;
}
</style>