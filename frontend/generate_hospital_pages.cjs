/**
 * Genera la estructura completa de paginas Nuxt para los modulos
 * del panel hospitalario (app), dentro de frontend/pages/app/.
 *
 * Ejecutar desde la carpeta frontend/:
 *     node generate_hospital_pages.cjs
 *
 * No sobreescribe archivos que ya existan.
 */
const fs = require('fs');
const path = require('path');

const MODULOS = [
  ['altas-pacientes',      'Altas de Pacientes'],
  ['consulta-externa',     'Consulta Externa'],
  ['archivo-clinico',      'Archivo Clinico'],
  ['agendamiento-citas',   'Agendamiento de Citas'],
  ['farmacia',             'Farmacia'],
  ['programacion-medica',  'Programacion Medica'],
  ['laboratorio',          'Laboratorio'],
  ['emergencia',           'Emergencia'],
  ['imagenologia',         'Imagenologia'],
  ['hospitalizacion',      'Hospitalizacion'],
  ['caja-facturacion',     'Caja y Facturacion'],
  ['sis-fua',              'SIS / FUA'],
  ['his',                  'HIS'],
  ['reportes',             'Reportes'],
  ['telemedicina',         'Telemedicina'],
  ['archivo',              'Archivo'],
  ['seguimiento-paciente', 'Seguimiento Paciente'],
  ['nutricion',            'Nutricion Pacientes'],
];

const BASE_DIR = path.join('pages', 'app');

function writeIfMissing(filePath, content) {
  if (fs.existsSync(filePath)) {
    console.log(`  (ya existe, se omite) ${filePath}`);
    return;
  }
  fs.writeFileSync(filePath, content, 'utf-8');
  console.log(`  creado: ${filePath}`);
}

function placeholderVue(nombre, tipo) {
  const titulo = tipo === 'index' ? nombre : tipo === 'create' ? `Crear - ${nombre}` : `Editar - ${nombre}`;
  return `<template>
  <div>
    <h1 class="text-lg font-semibold" style="color: var(--ink)">${titulo}</h1>
    <p class="text-sm mt-1" style="color: var(--ink-soft)">Esta seccion estara disponible proximamente.</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })
</script>
`;
}

function crearModulo(codigo, nombre) {
  const carpeta = path.join(BASE_DIR, codigo);
  fs.mkdirSync(carpeta, { recursive: true });
  console.log(`Modulo: ${codigo} (${nombre})`);

  writeIfMissing(path.join(carpeta, 'index.vue'), placeholderVue(nombre, 'index'));
  writeIfMissing(path.join(carpeta, 'create.vue'), placeholderVue(nombre, 'create'));
  writeIfMissing(path.join(carpeta, '[id].vue'), placeholderVue(nombre, 'id'));
}

function main() {
  if (!fs.existsSync('pages')) {
    console.log('ERROR: ejecuta este script desde la carpeta frontend/ (donde esta la carpeta pages/)');
    return;
  }

  fs.mkdirSync(BASE_DIR, { recursive: true });

  for (const [codigo, nombre] of MODULOS) {
    crearModulo(codigo, nombre);
  }

  console.log('\nListo. Revisa pages/app/. Si no existe un layout "app", habra que crearlo.');
}

main();