/**
 * Genera la estructura completa de paginas Nuxt para los 13 modulos
 * del panel hospitalario (app) que faltan, con sus submodulos reales,
 * dentro de frontend/pages/app/.
 *
 * Ejecutar desde la carpeta frontend/:
 *     node generate_hospital_pages_v2.cjs
 */
const fs = require('fs');
const path = require('path');

const MODULOS = {
  'cobros': ['Cobros', [
    ['cobro-por-paciente', 'Cobro por Paciente'],
    ['mi-caja', 'Mi Caja'],
  ]],
  'hospitalizacion': ['Hospitalizacion', [
    ['hospitalizaciones', 'Hospitalizaciones'],
    ['panel-camas', 'Panel de Camas'],
    ['seguimiento-paciente', 'Seguimiento Paciente'],
    ['censo-diario', 'Censo Diario'],
    ['interconsultas', 'Interconsultas'],
    ['consentimientos', 'Consentimientos Informados'],
  ]],
  'consulta-externa': ['Consulta Externa', [
    ['admision', 'Admision Consulta Externa'],
    ['programacion-medica', 'Programacion Medica'],
    ['calendario-medico', 'Calendario Medico'],
    ['triaje', 'Triaje'],
    ['atenciones-medicas', 'Atenciones Medicas'],
    ['bandeja-electronica', 'Bandeja Electronica'],
  ]],
  'emergencia': ['Emergencia', [
    ['admisiones', 'Admisiones'],
    ['observacion', 'Observacion'],
    ['referencias', 'Referencias'],
  ]],
  'laboratorio': ['Laboratorio', [
    ['ordenes', 'Ordenes de Laboratorio'],
  ]],
  'imagenologia': ['Imagenologia', [
    ['atenciones', 'Atenciones'],
    ['tickets', 'Tickets'],
    ['hospitalizados', 'Hospitalizados'],
    ['reimpresiones', 'Reimpresiones'],
  ]],
  'farmacia': ['Farmacia', [
    ['recetas-medicas', 'Recetas Medicas'],
    ['recetas-farmacotecnia', 'Recetas Farmacotecnia'],
    ['ventas-despacho', 'Ventas / Despacho'],
    ['notas-ingreso', 'Notas de Ingreso'],
    ['kardex-movimientos', 'Kardex / Movimientos'],
    ['notas-salida', 'Notas de Salida'],
    ['saldos', 'Saldos Farmacia'],
    ['reportes', 'Reportes'],
    ['panel-digemid', 'Panel DIGEMID'],
    ['ici-diario', 'ICI Diario'],
  ]],
  'caja': ['Caja', [
    ['comprobantes-pago', 'Comprobantes de Pago'],
    ['cuentas', 'Cuentas'],
  ]],
  'archivo-clinico': ['Archivo Clinico', [
    ['hc-electronica', 'HC Electronica'],
    ['historias-clinicas', 'Historias Clinicas'],
    ['movimientos-hc', 'Movimientos de H.C.'],
    ['personal-archivo', 'Personal de Archivo'],
  ]],
  'sis': ['SIS', [
    ['formato-fua', 'Formato FUA'],
    ['afiliaciones', 'Afiliaciones SIS'],
  ]],
  'his': ['HIS', [
    ['registro-microred', 'Registro HIS de la MicroRed'],
    ['formato-his', 'Formato HIS'],
  ]],
  'reportes': ['Reportes', [
    ['reporte-medico', 'Reporte por Medico'],
    ['reportes-hospitalizacion', 'Reportes de Hospitalizacion'],
  ]],
  'telemedicina': ['Telemedicina', [
    ['resumen-teleconsultas', 'Resumen Teleconsultas'],
    ['guia-rapida-minsa', 'Guia Rapida MINSA'],
  ]],
};

const BASE_DIR = path.join('pages', 'app');

function writeIfMissing(filePath, content) {
  if (fs.existsSync(filePath)) {
    console.log(`  (ya existe, se omite) ${filePath}`);
    return;
  }
  fs.writeFileSync(filePath, content, 'utf-8');
  console.log(`  creado: ${filePath}`);
}

function placeholderVue(nombreModulo, nombreSubmodulo, tipo) {
  const titulo = tipo === 'index'
    ? `${nombreModulo} - ${nombreSubmodulo}`
    : tipo === 'create'
      ? `Crear - ${nombreSubmodulo}`
      : `Editar - ${nombreSubmodulo}`;
  return `<template>
  <div>
    <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
      <span>${nombreModulo}</span><span>/</span><span>${nombreSubmodulo}</span>
    </div>
    <h1 class="text-lg font-semibold" style="color: var(--ink)">${titulo}</h1>
    <p class="text-sm mt-1" style="color: var(--ink-soft)">Esta seccion estara disponible proximamente.</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })
</script>
`;
}

function crearSubmodulo(carpetaModulo, nombreModulo, slug, nombreSubmodulo) {
  const carpeta = path.join(carpetaModulo, slug);
  fs.mkdirSync(carpeta, { recursive: true });

  writeIfMissing(path.join(carpeta, 'index.vue'), placeholderVue(nombreModulo, nombreSubmodulo, 'index'));
  writeIfMissing(path.join(carpeta, 'create.vue'), placeholderVue(nombreModulo, nombreSubmodulo, 'create'));
  writeIfMissing(path.join(carpeta, '[id].vue'), placeholderVue(nombreModulo, nombreSubmodulo, 'id'));
}

function crearModulo(codigo, nombre, submodulos) {
  const carpetaModulo = path.join(BASE_DIR, codigo);
  fs.mkdirSync(carpetaModulo, { recursive: true });
  console.log(`Modulo: ${codigo} (${nombre})`);

  for (const [slug, nombreSub] of submodulos) {
    crearSubmodulo(carpetaModulo, nombre, slug, nombreSub);
  }
}

function main() {
  if (!fs.existsSync('pages')) {
    console.log('ERROR: ejecuta este script desde la carpeta frontend/ (donde esta la carpeta pages/)');
    return;
  }

  fs.mkdirSync(BASE_DIR, { recursive: true });

  for (const codigo of Object.keys(MODULOS)) {
    const [nombre, submodulos] = MODULOS[codigo];
    crearModulo(codigo, nombre, submodulos);
  }

  console.log('\nListo. Revisa pages/app/.');
}

main();