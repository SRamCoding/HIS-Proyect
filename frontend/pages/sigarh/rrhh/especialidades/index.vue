<script setup lang="ts">
definePageMeta({ layout:'sigarh', middleware:['auth'] })
const { api } = useApi()
interface Item { id:string; nombre:string; codigo:string|null; descripcion:string|null; tipo:string; parent_id:string|null; parent_nombre:string|null; medicos_asignados:number; is_active:boolean; recomendada_nivel:boolean; hospital_level:string|null; es_oficial:boolean }
const items=ref<Item[]>([]), loading=ref(true), error=ref(''), search=ref(''), filtro=ref('all'), savingId=ref('')
const expanded=ref<Set<string>>(new Set())
const activeCount=computed(()=>items.value.filter(i=>i.is_active).length)
const specialties=computed(()=>items.value.filter(i=>i.tipo==='especialidad'))
const subspecialties=computed(()=>items.value.filter(i=>i.tipo==='subespecialidad'))
const hospitalLevel=computed(()=>items.value[0]?.hospital_level||'Sin categoría')
const normalizedSearch=computed(()=>search.value.trim().toLocaleLowerCase('es'))
function passes(item:Item) {
  if(filtro.value==='active'&&!item.is_active)return false
  if(filtro.value==='inactive'&&item.is_active)return false
  if(filtro.value==='recommended'&&!item.recomendada_nivel)return false
  const q=normalizedSearch.value
  return !q||`${item.nombre} ${item.codigo||''}`.toLocaleLowerCase('es').includes(q)
}
function children(parent:Item){return subspecialties.value.filter(s=>s.parent_id===parent.id)}
const groups=computed(()=>specialties.value.filter(parent=>passes(parent)||children(parent).some(passes)))
function visibleChildren(parent:Item){const all=children(parent); return normalizedSearch.value||filtro.value!=='all'?all.filter(passes):all}
function isOpen(id:string){return expanded.value.has(id)||!!normalizedSearch.value}
function toggle(id:string){const next=new Set(expanded.value); next.has(id)?next.delete(id):next.add(id); expanded.value=next}
async function cargar(){loading.value=true;error.value='';try{items.value=await api<Item[]>('/sigarh/rrhh/especialidades')}catch(e:any){error.value=apiErr(e,'No se pudo cargar el catálogo')}finally{loading.value=false}}
async function cambiarEstado(item:Item){savingId.value=item.id;error.value='';try{Object.assign(item,await api<Item>(`/sigarh/rrhh/especialidades/${item.id}`,{method:'PATCH',body:{is_active:!item.is_active}}))}catch(e:any){error.value=apiErr(e,'No se pudo actualizar la cartera')}finally{savingId.value=''}}
onMounted(cargar)
</script>

<template><div class="sigarh-index-container">
  <div class="sigarh-page-header"><div class="sigarh-header-left"><div class="sigarh-header-icon" style="background:var(--purple-soft)"><UIcon name="i-heroicons-academic-cap" class="w-5 h-5" style="color:var(--purple)" /></div><div><h1 class="page-title">Especialidades y subespecialidades</h1><p class="page-subtitle">Cartera hospitalaria organizada por especialidad principal</p></div></div><div class="flex items-center gap-3"><span class="badge badge--info">Categoría {{ hospitalLevel }}</span><NuxtLink to="/sigarh/rrhh/especialidades/create" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva especialidad</NuxtLink></div></div>
  <div class="sigarh-stats-grid">
    <div class="sigarh-stat-card" style="border-left-color:var(--purple)"><div><div class="sigarh-stat-value">{{ specialties.length }}</div><div class="sigarh-stat-label">Especialidades</div></div></div>
    <div class="sigarh-stat-card" style="border-left-color:var(--navy)"><div><div class="sigarh-stat-value">{{ subspecialties.length }}</div><div class="sigarh-stat-label">Subespecialidades</div></div></div>
    <div class="sigarh-stat-card" style="border-left-color:var(--green)"><div><div class="sigarh-stat-value">{{ activeCount }}</div><div class="sigarh-stat-label">Opciones en cartera</div></div></div>
    <div class="sigarh-stat-card" style="border-left-color:var(--amber)"><div><div class="sigarh-stat-value">{{ items.reduce((n,i)=>n+i.medicos_asignados,0) }}</div><div class="sigarh-stat-label">Asignaciones RR. HH.</div></div></div>
  </div>
  <div class="mb-4 rounded-xl border p-4 text-sm" style="background:#eff6ff;border-color:#bfdbfe;color:#1e3a5f"><strong>Selecciona una especialidad para ver sus subespecialidades.</strong> SIGARH administra esta cartera y APP utiliza solamente las opciones activas.</div>
  <div class="sigarh-table-container">
    <div class="sigarh-filter-bar"><div class="sigarh-filter-left"><div class="sigarh-search-wrapper"><UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" /><input v-model="search" class="sigarh-search-input" placeholder="Buscar especialidad o subespecialidad..." /></div><div class="sigarh-filter-group"><button v-for="option in [{k:'all',n:'Todas'},{k:'active',n:'En cartera'},{k:'recommended',n:'Sugeridas'},{k:'inactive',n:'No activas'}]" :key="option.k" class="sigarh-filter-btn" :class="{active:filtro===option.k}" @click="filtro=option.k">{{ option.n }}</button></div></div><span class="sigarh-result-count">{{ groups.length }} especialidades</span></div>
    <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" /><p>Cargando catálogo...</p></div>
    <div v-else-if="error" class="sigarh-table-state"><p style="color:var(--alert)">{{ error }}</p><button class="btn-outline" @click="cargar">Reintentar</button></div>
    <div v-else-if="!groups.length" class="sigarh-table-state"><p>No hay coincidencias con estos filtros.</p></div>
    <div v-else class="divide-y">
      <section v-for="parent in groups" :key="parent.id" class="p-4">
        <div class="flex items-center gap-4">
          <button type="button" class="w-9 h-9 rounded-lg border flex items-center justify-center shrink-0" :aria-expanded="isOpen(parent.id)" @click="toggle(parent.id)"><UIcon :name="isOpen(parent.id)?'i-heroicons-chevron-down':'i-heroicons-chevron-right'" class="w-4 h-4" /></button>
          <div class="sigarh-item-icon" style="background:var(--purple-soft)"><UIcon name="i-heroicons-academic-cap" class="w-4 h-4" style="color:var(--purple)" /></div>
          <button type="button" class="flex-1 text-left" @click="toggle(parent.id)"><div class="flex flex-wrap items-center gap-2"><span class="sigarh-item-name">{{ parent.nombre }}</span><span v-if="parent.es_oficial" class="badge badge--neutral">Oficial</span><span v-else class="badge badge--info">Hospital</span><span v-if="parent.recomendada_nivel" class="badge badge--info">Sugerida {{ hospitalLevel }}</span></div><div class="text-xs mt-1" style="color:var(--ink-soft)">{{ parent.codigo }} · {{ children(parent).length }} subespecialidades · {{ parent.medicos_asignados }} asignaciones</div></button>
          <NuxtLink :to="`/sigarh/rrhh/especialidades/${parent.id}`" class="sigarh-action-btn" title="Ver o editar"><UIcon name="i-heroicons-pencil-square" class="w-4 h-4" /></NuxtLink>
          <div class="text-right"><button class="toggle-switch" :class="{'toggle-active':parent.is_active}" :disabled="savingId===parent.id" @click="cambiarEstado(parent)"><span class="toggle-slider" /></button><div class="text-xs mt-1" :style="{color:parent.is_active?'var(--green)':'var(--ink-soft)'}">{{ parent.is_active?'En cartera':'No activa' }}</div></div>
        </div>
        <div v-if="isOpen(parent.id)" class="mt-4 ml-12 rounded-xl border overflow-hidden">
          <div class="px-4 py-3 flex items-center justify-between" style="background:var(--surface-soft)"><strong class="text-sm">Subespecialidades</strong><NuxtLink :to="`/sigarh/rrhh/especialidades/create?tipo=subespecialidad&parent_id=${parent.id}`" class="text-sm hover:underline" style="color:var(--teal)">+ Agregar subespecialidad</NuxtLink></div>
          <div v-if="!visibleChildren(parent).length" class="p-4 text-sm" style="color:var(--ink-soft)">No hay subespecialidades registradas.</div>
          <div v-for="child in visibleChildren(parent)" :key="child.id" class="px-4 py-3 border-t flex items-center gap-3"><UIcon name="i-heroicons-arrow-turn-down-right" class="w-4 h-4" style="color:var(--navy)" /><div class="flex-1"><NuxtLink :to="`/sigarh/rrhh/especialidades/${child.id}`" class="font-medium hover:underline">{{ child.nombre }}</NuxtLink><div class="text-xs" style="color:var(--ink-soft)">{{ child.codigo }} · {{ child.medicos_asignados }} asignaciones <span v-if="child.es_oficial">· CONAREME</span></div></div><button class="toggle-switch" :class="{'toggle-active':child.is_active}" :disabled="savingId===child.id" @click="cambiarEstado(child)"><span class="toggle-slider" /></button></div>
        </div>
      </section>
    </div>
    <div class="sigarh-table-footer">Las denominaciones oficiales se conservan; el hospital puede agregar registros propios cuando su cartera lo requiera.</div>
  </div>
</div></template>
