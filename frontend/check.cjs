// frontend/check.js
const fs = require('fs');
const { parse } = require('@vue/compiler-sfc');

const path = process.argv[2];
const source = fs.readFileSync(path, 'utf-8');
const { errors } = parse(source, { filename: path });

if (errors.length) {
  console.log('ERRORES ENCONTRADOS:');
  errors.forEach(e => {
    console.log('---');
    console.log(e.message);
    if (e.loc) {
      console.log('Linea:', e.loc.start.line, 'Columna:', e.loc.start.column);
    }
  });
} else {
  console.log('Sin errores de parseo del SFC.');
}