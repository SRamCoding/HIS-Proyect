<template>
  <button class="btn-primary" :disabled="saving" @click="$emit('save')">
    <UIcon v-if="saving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
    <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
    {{ saving ? savingText : saveText }}
  </button>
  <button v-if="showCreateAnother" class="btn-outline" :disabled="saving" @click="$emit('saveAnother')">
    <UIcon name="i-heroicons-plus" class="w-4 h-4" />
    Crear y otro
  </button>
  <NuxtLink :to="cancelTo" class="btn-cancel">Cancelar</NuxtLink>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  saving?: boolean
  saveText?: string
  savingText?: string
  cancelTo: string
  showCreateAnother?: boolean
}>(), {
  saveText: 'Guardar',
  savingText: 'Guardando...',
  showCreateAnother: false,
})

defineEmits(['save', 'saveAnother'])
</script>
