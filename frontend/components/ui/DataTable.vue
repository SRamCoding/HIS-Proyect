<!-- components/ui/DataTable.vue -->
<template>
  <div class="table-card" :style="{
    background: 'var(--paper)',
    border: '1px solid var(--line)',
    borderRadius: 'var(--radius-lg)',
    boxShadow: 'var(--shadow-card)',
    overflow: 'hidden'
  }">
    <div v-if="$slots.toolbar" class="table-toolbar" :style="{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--line)' }">
      <slot name="toolbar" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="table-state" :style="{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem', gap: '1rem' }">
      <div class="loading-spinner" :style="{ animation: 'spin 1s linear infinite' }">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6" style="color: var(--teal)" />
      </div>
      <p style="color: var(--ink-soft)">{{ loadingText || 'Cargando...' }}</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="table-state" :style="{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem', gap: '1rem' }">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
      <p style="color: var(--alert)">{{ error }}</p>
      <button class="btn-secondary" @click="$emit('retry')" :style="{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '0.5rem 1rem',
        borderRadius: '6px',
        fontSize: '0.8125rem',
        fontWeight: 500,
        border: '1px solid var(--line)',
        background: 'var(--paper)',
        color: 'var(--ink)',
        cursor: 'pointer'
      }">Reintentar</button>
    </div>

    <!-- Empty -->
    <div v-else-if="!data?.length" class="table-state" :style="{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem', gap: '1rem' }">
      <div class="empty-icon" :style="{ width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--mist)' }">
        <UIcon :name="emptyIcon || 'i-heroicons-document-text'" class="w-12 h-12" style="color: var(--ink-soft)" />
      </div>
      <h3 style="font-size: 1.125rem; color: var(--ink); margin: 0">{{ emptyTitle || 'No hay registros' }}</h3>
      <p style="color: var(--ink-soft); margin: 0">{{ emptyMessage || 'Comienza creando un nuevo registro' }}</p>
      <slot name="empty-action" />
    </div>

    <!-- Table -->
    <div v-else class="table-responsive" :style="{ overflowX: 'auto' }">
      <table class="data-table" :style="{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }">
        <thead :style="{ background: 'var(--mist)' }">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              class="table-header"
              :style="{
                padding: '0.75rem 1rem',
                textAlign: column.align || 'left',
                fontWeight: 600,
                color: 'var(--ink-soft)',
                fontSize: '0.75rem',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                borderBottom: '1px solid var(--line)',
                width: column.width || 'auto'
              }"
            >
              <div class="th-content" :style="{ display: 'flex', alignItems: 'center', gap: '0.25rem', justifyContent: column.align === 'right' ? 'flex-end' : 'flex-start' }">
                <UIcon v-if="column.icon" :name="column.icon" class="w-3.5 h-3.5" />
                {{ column.label }}
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in data"
            :key="rowKey(row)"
            class="table-row"
            :style="{ borderBottom: '1px solid var(--line)', transition: 'background 0.15s ease', cursor: clickable ? 'pointer' : 'default' }"
            @click="clickable ? $emit('row-click', row) : undefined"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              class="table-cell"
              :style="{
                padding: '0.875rem 1rem',
                verticalAlign: 'middle',
                textAlign: column.align || 'left',
                color: column.color ? column.color(row) : 'var(--ink)'
              }"
            >
              <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
                <span v-if="column.badge" class="badge" :class="column.badge(row)" :style="{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.375rem',
                  padding: '0.25rem 0.625rem',
                  borderRadius: '20px',
                  fontSize: '0.75rem',
                  fontWeight: 500
                }">
                  <span v-if="column.badgeDot" class="badge-dot" :style="{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    display: 'inline-block',
                    background: column.badgeDot(row)
                  }" />
                  {{ row[column.key] || '—' }}
                </span>
                <template v-else>
                  {{ row[column.key] || '—' }}
                </template>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Footer -->
    <div v-if="data?.length && ($slots.footer || showFooter)" class="table-footer" :style="{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0.75rem 1.5rem',
      borderTop: '1px solid var(--line)',
      flexWrap: 'wrap',
      gap: '0.5rem'
    }">
      <slot name="footer">
        <span class="footer-info" style="font-size: 0.8125rem; color: var(--ink-soft)">
          Mostrando <strong>{{ data.length }}</strong> de <strong>{{ totalCount || data.length }}</strong> registros
        </span>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Column {
  key: string
  label: string
  icon?: string
  align?: 'left' | 'center' | 'right'
  width?: string
  badge?: (row: any) => string
  badgeDot?: (row: any) => string
  color?: (row: any) => string
}

const props = defineProps<{
  data: any[]
  columns: Column[]
  loading?: boolean
  loadingText?: string
  error?: string
  emptyIcon?: string
  emptyTitle?: string
  emptyMessage?: string
  clickable?: boolean
  totalCount?: number
  showFooter?: boolean
}>()

defineEmits<{
  (e: 'retry'): void
  (e: 'row-click', row: any): void
}>()

// key estable por fila: usa id si existe, si no cae a JSON.stringify
// (evita que Vue reutilice nodos DOM por posición al filtrar/buscar)
const rowKey = (row: any) => row?.id ?? JSON.stringify(row)
</script>

<style scoped>
.table-row:hover {
  background: var(--mist);
}
.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>