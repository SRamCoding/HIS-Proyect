<template>
  <div class="space-y-5 p-5">
    <div><h1 class="text-2xl font-bold">{{ title }}</h1><p class="text-sm text-gray-500">Farmacia hospitalaria · SISMED / DIGEMID</p></div>
    <UAlert v-if="error" color="error" :title="error" icon="i-heroicons-exclamation-triangle" />
    <UCard>
      <div class="grid gap-3 md:grid-cols-5">
        <USelect v-if="needsWarehouse" v-model="filters.almacen_id" :items="warehouseOptions" placeholder="Almacén / farmacia" />
        <UInput v-model="filters.fecha_desde" type="date" /><UInput v-model="filters.fecha_hasta" type="date" />
        <UInput v-model="filters.q" placeholder="Documento, receta o producto" />
        <UButton icon="i-heroicons-magnifying-glass" :loading="loading" @click="load">Buscar</UButton>
      </div>
      <div class="mt-3 flex gap-2">
        <UButton v-if="isMovement" icon="i-heroicons-plus" @click="showForm=true">{{ mode==='venta-farmacia'?'Nueva venta':'Nueva nota' }}</UButton>
        <UButton v-if="mode==='farmacotecnia'" icon="i-heroicons-plus" @click="showForm=true">Nueva preparación</UButton>
        <UButton v-if="isReport" icon="i-heroicons-document-arrow-down" variant="outline" @click="download('pdf')">PDF</UButton>
        <UButton v-if="isReport" icon="i-heroicons-table-cells" variant="outline" @click="download('csv')">CSV</UButton>
      </div>
    </UCard>

    <UCard v-if="showForm && mode==='farmacotecnia'">
      <template #header><b>Nueva orden de Farmacotecnia</b></template>
      <div class="grid gap-3 md:grid-cols-3"><USelect v-model="pharma.tipo_requerimiento" :items="['REDOSIFICACIÓN','FÓRMULA MAGISTRAL O GALÉNICA']" /><UInput v-model="pharma.formula" placeholder="Fórmula / preparación" /><UInput v-model.number="pharma.cantidad" type="number" min="1" /><UInput v-model="pharma.unidad" placeholder="Unidad" /><UInput v-model="pharma.via_administracion" placeholder="Vía de administración" /><UInput v-model.number="pharma.estabilidad_horas" type="number" placeholder="Estabilidad (horas)" /><UTextarea v-model="pharma.condiciones_conservacion" placeholder="Conservación" /><UTextarea v-model="pharma.observaciones" placeholder="Observaciones" /></div>
      <div class="mt-4 flex justify-end"><UButton @click="savePharma">Guardar</UButton></div>
    </UCard>

    <UCard v-if="showForm && isMovement">
      <template #header><b>Nueva {{ title }}</b></template>
      <div class="grid gap-3 md:grid-cols-4">
        <USelect v-if="!isIngreso" v-model="form.almacen_origen_id" :items="warehouseOptions" placeholder="Almacén / farmacia de origen *" />
        <USelect v-model="form.almacen_destino_id" :items="destinationOptions" :placeholder="isIngreso?'Almacén / farmacia de destino *':'Destino (solo transferencia)'" />
        <USelect v-model="form.concepto" :items="conceptOptions" placeholder="Concepto del movimiento *" />
        <UInput v-model="form.numero_documento" placeholder="N.º documento" />
        <UInput v-model="form.numero_documento_origen" placeholder="Documento origen" />
        <UInput v-model="form.numero_cuenta" placeholder="N.º cuenta paciente" />
        <UInput v-model="form.fuente_financiamiento" placeholder="SIS / particular / estrategia" list="farmacia-seguros" />
        <datalist id="farmacia-seguros">
          <option v-for="s in seguros" :key="s.id" :value="s.nombre" />
        </datalist>
        <UInput v-model="form.observaciones" placeholder="Observaciones" />
      </div>
      <div class="mt-4 grid gap-2 md:grid-cols-7">
        <USelect v-if="isIngreso" v-model="line.medicamento_id" :items="medicineOptions" placeholder="Medicamento *" class="md:col-span-2" />
        <USelect v-else v-model="line.lote_id" :items="stockOptions" placeholder="Medicamento y lote disponible *" class="md:col-span-3" @update:model-value="selectStockLot" />
        <UInput v-if="isIngreso" v-model="line.numero_lote" placeholder="Lote *" /><UInput v-if="isIngreso" v-model="line.fecha_vencimiento" type="date" :min="today" />
        <div v-else class="self-center text-sm text-gray-600">Disponible: <b>{{ selectedStock?.stock ?? 0 }}</b></div>
        <UInput v-model.number="line.cantidad" type="number" min="0.0001" placeholder="Cantidad" />
        <UInput v-model.number="line.precio_unitario" type="number" min="0" step="0.0001" placeholder="Precio" />
        <UButton @click="addLine">Añadir</UButton>
      </div>
      <UAlert v-if="formError" class="mt-3" color="warning" :title="formError" />
      <UTable class="mt-3" :data="form.items" :columns="itemColumns" />
      <div class="mt-4 flex justify-end gap-2"><UButton variant="ghost" @click="showForm=false">Cancelar</UButton><UButton :loading="saving" :disabled="!canSaveMovement" @click="saveMovement">Confirmar movimiento</UButton></div>
    </UCard>

    <UCard>
      <UTable :data="rows" :columns="columns" :loading="loading">
        <template #acciones-cell="{ row }"><UButton size="xs" variant="soft" @click="openDetail(row.original)">Detalle</UButton></template>
      </UTable>
      <div v-if="!rows.length && !loading" class="py-8 text-center text-gray-500">No hay registros con estos filtros.</div>
    </UCard>

    <UModal v-model:open="detailOpen"><template #content><UCard><template #header><b>Detalle</b></template>
      <div v-if="mode==='recetas'" class="space-y-3"><p><b>{{ detail.numero }}</b> · {{ detail.estado }}</p><USelect v-model="dispenseWarehouse" :items="warehouseOptions" placeholder="Farmacia que dispensa"/><div v-for="item in detail.items" :key="item.id" class="grid grid-cols-3 gap-2"><span class="col-span-2 text-sm">{{ item.codigo }} · {{ item.nombre }} (prescrito: {{ item.cantidad }})</span><UInput v-model.number="item.a_dispensar" type="number" min="0" :max="item.cantidad" /></div><UButton :disabled="!dispenseWarehouse" @click="dispenseRecipe">Dispensar por FEFO</UButton></div>
      <div v-else-if="isMovement" class="space-y-3">
        <p><b>{{ detail.numero }}</b> · {{ detail.concepto }} · {{ detail.estado }}</p>
        <p v-if="detail.paciente" class="text-sm text-gray-600">Paciente: {{ detail.paciente }} ({{ detail.paciente_dni || 'NN' }})</p>
        <div v-if="detail.concepto==='VENTA'" class="text-sm">
          Total S/ {{ Number(detail.total || 0).toFixed(2) }} ·
          <span :class="{'text-green-600':detail.estado_pago==='pagado','text-amber-600':detail.estado_pago==='parcial','text-red-600':detail.estado_pago==='pendiente'}">
            {{ detail.estado_pago==='pagado' ? 'Pagado' : detail.estado_pago==='parcial' ? 'Pago parcial' : 'Pendiente de pago' }}
          </span>
          <span v-if="detail.estado_pago!=='pagado'" class="text-gray-500">(S/ {{ Number(detail.monto_pendiente || 0).toFixed(2) }} pendiente · cobrar en Caja)</span>
        </div>
        <table class="w-full text-sm"><thead><tr><th class="text-left">Medicamento</th><th class="text-left">Lote</th><th class="text-left">Vence</th><th class="text-right">Cantidad</th><th class="text-right">Precio</th></tr></thead>
          <tbody><tr v-for="item in detail.items" :key="item.id"><td>{{ item.descripcion }}</td><td>{{ item.numero_lote }}</td><td>{{ item.fecha_vencimiento }}</td><td class="text-right">{{ item.cantidad }}</td><td class="text-right">{{ Number(item.precio_unitario).toFixed(4) }}</td></tr></tbody>
        </table>
      </div>
      <pre v-else class="max-h-[65vh] overflow-auto whitespace-pre-wrap text-xs">{{ JSON.stringify(detail,null,2) }}</pre></UCard></template></UModal>
  </div>
</template>
<script setup lang="ts">
const props=defineProps<{mode:string}>(); const {api}=useApi()
const loading=ref(false),saving=ref(false),error=ref(''),formError=ref(''),rows=ref<any[]>([]),warehouses=ref<any[]>([]),medicines=ref<any[]>([]),seguros=ref<any[]>([]),stockRows=ref<any[]>([]),showForm=ref(false),detailOpen=ref(false),detail=ref<any>({})
const today=new Date().toISOString().slice(0,10)
const filters=reactive({almacen_id:'',fecha_desde:new Date().toISOString().slice(0,10),fecha_hasta:new Date().toISOString().slice(0,10),q:''})
const map:any={recetas:'Recetas','ingreso-almacen':'Nota de Ingreso Almacén','salida-almacen':'Nota de Salida Almacén','ingreso-farmacia':'Nota de Ingreso Farmacia','salida-farmacia':'Nota de Salida Farmacia',medicamentos:'Medicamentos',farmacotecnia:'Farmacotecnia','ici-diario':'ICI Diario','idi-diario':'IDI Diario',saldos:'Saldos Farmacia',kardex:'Kardex','saldo-almacen':'Saldo Almacén',digemid:'DIGEMID','venta-farmacia':'Venta Farmacia'}
const title=computed(()=>map[props.mode]||'Farmacia'); const isMovement=computed(()=>props.mode.includes('ingreso')||props.mode.includes('salida')||props.mode==='venta-farmacia'); const isReport=computed(()=>['medicamentos','ici-diario','idi-diario','saldos','kardex','saldo-almacen','digemid'].includes(props.mode)); const needsWarehouse=computed(()=>props.mode!=='recetas')
const isIngreso=computed(()=>props.mode.includes('ingreso'))
const conceptOptions=computed(()=>props.mode==='venta-farmacia'?['VENTA']:isIngreso.value?['COMPRA','TRANSFERENCIA','DEVOLUCIÓN','DONACIÓN','AJUSTE DE INVENTARIO']:['DISTRIBUCIÓN','TRANSFERENCIA','DISPENSACIÓN','DEVOLUCIÓN','MERMA','AJUSTE DE INVENTARIO'])
const warehouseOptions=computed(()=>warehouses.value.map(x=>({label:`${x.codigo} - ${x.nombre}`,value:x.id}))); const medicineOptions=computed(()=>medicines.value.map(x=>({label:`${x.codigo} - ${x.nombre}`,value:x.id})))
const destinationOptions=computed(()=>warehouseOptions.value.filter(x=>x.value!==form.almacen_origen_id))
const stockOptions=computed(()=>stockRows.value.map(x=>({label:`${x.codigo} - ${x.medicamento} · lote ${x.lote} · stock ${x.stock}`,value:x.lote_id})))
const selectedStock=computed(()=>stockRows.value.find(x=>x.lote_id===line.lote_id))
const movementInfo=computed(()=>({tipo:props.mode.includes('ingreso')?'INGRESO':'SALIDA',ambito:props.mode.includes('almacen')?'ALMACEN':'FARMACIA'}))
const form=reactive<any>({concepto:'',almacen_origen_id:'',almacen_destino_id:'',numero_documento:'',numero_documento_origen:'',numero_cuenta:'',fuente_financiamiento:'',observaciones:'',items:[]}); const line=reactive<any>({lote_id:'',medicamento_id:'',numero_lote:'',fecha_vencimiento:'',cantidad:1,precio_unitario:0})
const pharma=reactive<any>({tipo_requerimiento:'REDOSIFICACIÓN',formula:'',cantidad:1,unidad:'UNIDAD',via_administracion:'',estabilidad_horas:null,condiciones_conservacion:'',observaciones:''});const dispenseWarehouse=ref('')
const itemColumns=[{accessorKey:'medicamento_nombre',header:'Medicamento'},{accessorKey:'numero_lote',header:'Lote'},{accessorKey:'fecha_vencimiento',header:'Vencimiento'},{accessorKey:'cantidad',header:'Cantidad'},{accessorKey:'precio_unitario',header:'Precio'}]
const columns=computed(()=>{if(props.mode==='recetas')return [{accessorKey:'numero',header:'Receta'},{accessorKey:'paciente',header:'Paciente'},{accessorKey:'documento',header:'Documento'},{accessorKey:'servicio',header:'Servicio'},{accessorKey:'estado',header:'Estado'},{id:'acciones',header:'Acciones'}]; if(isMovement.value)return [{accessorKey:'numero',header:'Movimiento'},{accessorKey:'created_at',header:'Fecha'},{accessorKey:'concepto',header:'Concepto'},{accessorKey:'estado',header:'Estado'},{accessorKey:'total',header:'Total'},{id:'acciones',header:'Acciones'}]; return [{accessorKey:'codigo',header:'Código'},{accessorKey:'medicamento',header:'Medicamento'},{accessorKey:'almacen',header:'Almacén'},{accessorKey:'lote',header:'Lote'},{accessorKey:'vencimiento',header:'Vencimiento'},{accessorKey:'stock',header:'Cantidad'},{accessorKey:'valor',header:'Valor'}]})
const canSaveMovement=computed(()=>Boolean(form.concepto&&form.items.length&&(isIngreso.value?form.almacen_destino_id:form.almacen_origen_id)))
function selectStockLot(id:string){const stock=stockRows.value.find(x=>x.lote_id===id);if(stock)Object.assign(line,{lote_id:stock.lote_id,medicamento_id:stock.medicamento_id,numero_lote:stock.lote,fecha_vencimiento:stock.vencimiento,precio_unitario:stock.costo,cantidad:1})}
async function loadStock(){stockRows.value=[];Object.assign(line,{lote_id:'',medicamento_id:'',numero_lote:'',fecha_vencimiento:'',cantidad:1,precio_unitario:0});if(!isIngreso.value&&form.almacen_origen_id)stockRows.value=await api('/app/farmacia/saldos',{query:{almacen_id:form.almacen_origen_id}})}
function addLine(){formError.value='';if(!line.medicamento_id)return void(formError.value=isIngreso.value?'Selecciona un medicamento.':'Selecciona un lote con stock disponible.');if(!line.numero_lote.trim())return void(formError.value='Ingresa el número de lote.');if(!line.fecha_vencimiento)return void(formError.value='Ingresa la fecha de vencimiento.');if(line.fecha_vencimiento<today)return void(formError.value='El lote está vencido; no puede incorporarse al stock disponible.');if(!(Number(line.cantidad)>0))return void(formError.value='La cantidad debe ser mayor que cero.');if(!isIngreso.value&&Number(line.cantidad)>Number(selectedStock.value?.stock||0))return void(formError.value=`La cantidad supera el stock disponible (${selectedStock.value?.stock||0}).`);const med=medicines.value.find(x=>x.id===line.medicamento_id);form.items.push({...line,medicamento_nombre:med?`${med.codigo} - ${med.nombre}`:line.medicamento_id});Object.assign(line,{lote_id:'',medicamento_id:'',numero_lote:'',fecha_vencimiento:'',cantidad:1,precio_unitario:0})}
function errorMessage(e:any, fallback:string){const detail=e?.data?.detail??e?.response?._data?.detail??e?.response?.data?.detail;if(Array.isArray(detail))return detail.map((x:any)=>x.msg).join('. ');return typeof detail==='string'?detail:fallback}
async function load(){loading.value=true;error.value='';try{if(props.mode==='recetas')rows.value=await api('/app/farmacia/recetas',{query:{q:filters.q||undefined}});else if(isMovement.value){const r:any=await api('/app/farmacia/movimientos',{query:{...movementInfo.value,almacen_id:filters.almacen_id||undefined,fecha_desde:filters.fecha_desde,fecha_hasta:filters.fecha_hasta,q:filters.q||undefined,concepto:props.mode==='venta-farmacia'?'VENTA':undefined}});rows.value=r.items}else if(props.mode==='farmacotecnia')rows.value=await api('/app/farmacia/farmacotecnia');else rows.value=await api(`/app/farmacia/reportes/${props.mode}/datos`,{query:{fecha_desde:filters.fecha_desde,fecha_hasta:filters.fecha_hasta,almacen_id:filters.almacen_id||undefined,q:filters.q||undefined}})}catch(e:any){error.value=errorMessage(e,'No se pudo cargar la información')}finally{loading.value=false}}
async function saveMovement(){formError.value='';if(!form.concepto)return void(formError.value='Selecciona el concepto del movimiento.');if(isIngreso.value&&!form.almacen_destino_id)return void(formError.value='Selecciona el almacén o farmacia de destino.');if(!isIngreso.value&&!form.almacen_origen_id)return void(formError.value='Selecciona el almacén o farmacia de origen.');if(!form.items.length)return void(formError.value='Añade por lo menos un medicamento a la nota.');saving.value=true;error.value='';try{const items=form.items.map(({medicamento_nombre,...item}:any)=>item);await api('/app/farmacia/movimientos',{method:'POST',body:{...form,items,concepto:props.mode==='venta-farmacia'?'VENTA':form.concepto,...movementInfo.value,almacen_origen_id:isIngreso.value?null:form.almacen_origen_id||null,almacen_destino_id:form.almacen_destino_id||null,confirmar:true}});showForm.value=false;form.items=[];await load()}catch(e:any){formError.value=errorMessage(e,'No se pudo guardar el movimiento')}finally{saving.value=false}}
async function savePharma(){await api('/app/farmacia/farmacotecnia',{method:'POST',body:pharma});showForm.value=false;await load()}
async function dispenseRecipe(){const items=detail.value.items.filter((x:any)=>x.a_dispensar>0).map((x:any)=>({receta_item_id:x.id,cantidad:x.a_dispensar}));if(!items.length)return;await api(`/app/farmacia/recetas/${detail.value.id}/dispensar`,{method:'POST',body:{almacen_id:dispenseWarehouse.value,items}});detailOpen.value=false;await load()}
async function openDetail(row:any){detail.value=isMovement.value?await api(`/app/farmacia/movimientos/${row.id}`):props.mode==='recetas'?await api(`/app/farmacia/recetas/${row.id}`):row;detailOpen.value=true}
async function download(ext:string){const blob:any=await api(`/app/farmacia/reportes/${props.mode}.${ext}`,{query:{fecha_desde:filters.fecha_desde,fecha_hasta:filters.fecha_hasta,almacen_id:filters.almacen_id||undefined,q:filters.q||undefined},responseType:'blob'});const url=URL.createObjectURL(blob);window.open(url,'_blank');setTimeout(()=>URL.revokeObjectURL(url),60000)}
onMounted(async()=>{try{[warehouses.value,medicines.value,seguros.value]=await Promise.all([api('/app/farmacia/catalogos/almacenes'),api('/app/farmacia/catalogos/medicamentos'),api('/app/farmacia/catalogos/seguros')])}finally{load()}})
watch(()=>form.almacen_origen_id,()=>{if(form.almacen_destino_id===form.almacen_origen_id)form.almacen_destino_id='';loadStock()})
</script>
