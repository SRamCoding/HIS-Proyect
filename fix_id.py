with open('[id].vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Agregar pisos ref
content = content.replace(
    'const departamentos = ref<any[]>([])',
    'const departamentos = ref<any[]>([])\nconst pisos = ref<any[]>([])'
)

# 2. Agregar piso_id al form
content = content.replace(
    "  departamento_id: '',\n  is_active: true,\n})",
    "  departamento_id: '',\n  piso_id: '',\n  is_active: true,\n})"
)

# 3. Agregar pisoSeleccionado computed
content = content.replace(
    'const departamentoSeleccionado = computed(() =>\n  departamentos.value.find(d => d.id === form.departamento_id)\n)',
    'const departamentoSeleccionado = computed(() =>\n  departamentos.value.find(d => d.id === form.departamento_id)\n)\n\nconst pisoSeleccionado = computed(() =>\n  pisos.value.find(p => p.id === form.piso_id)\n)'
)

# 4. Agregar piso_id en el PATCH body
content = content.replace(
    '        departamento_id: form.departamento_id || null,\n        is_active: form.is_active,',
    '        departamento_id: form.departamento_id || null,\n        piso_id: form.piso_id || null,\n        is_active: form.is_active,'
)

# 5. Cargar piso en onMounted
content = content.replace(
    '      api<any[]>(\'/sigarh/mantenimiento/departamentos\'),\n    ])',
    '      api<any[]>(\'/sigarh/mantenimiento/departamentos\'),\n      api<any[]>(\'/sigarh/infraestructura-hosp/pisos\'),\n    ])'
)

content = content.replace(
    '    const [data, deps] = await Promise.all([',
    '    const [data, deps, pisosData] = await Promise.all(['
)

# 6. Asignar valores del form al cargar
content = content.replace(
    '    form.departamento_id = data.departamento_id || \'\'\n    form.is_active = data.is_active\n    departamentos.value = deps',
    '    form.departamento_id = data.departamento_id || \'\'\n    form.piso_id = data.piso_id || \'\'\n    form.is_active = data.is_active\n    departamentos.value = deps\n    pisos.value = pisosData'
)

# 7. Agregar select de piso en template
content = content.replace(
    '''              <div class="form-group">
                <label class="form-label">Departamento</label>''',
    '''              <div class="form-group">
                <label class="form-label">Piso</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-building-office-2" class="input-icon" />
                  <select v-model="form.piso_id" class="input-clinical">
                    <option value="">Sin piso</option>
                    <option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                  </select>
                </div>
                <p class="field-hint">Piso hospitalario donde se ubica el servicio</p>
              </div>

              <div class="form-group">
                <label class="form-label">Departamento</label>'''
)

with open('[id].vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Listo')
