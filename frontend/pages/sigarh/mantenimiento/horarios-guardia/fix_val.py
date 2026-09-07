with open('create.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Eliminar validacion de hora_fin posterior a hora_inicio
content = content.replace(
    "    if (form.hora_inicio && form.hora_fin && form.hora_inicio >= form.hora_fin) {\n      errors.hora_fin = 'La hora de fin debe ser posterior a la hora de inicio'\n      valid = false\n    }",
    ""
)

# Eliminar validacion de hora_fin requerida (ya no es editable)
content = content.replace(
    "    if (!form.hora_fin) {\n      errors.hora_fin = 'La hora de fin es requerida'\n      valid = false\n    }\n",
    ""
)

with open('create.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Listo')
