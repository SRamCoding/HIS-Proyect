with open('create.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar los 4 bloques
import re

# Extraer cada bloque
def extract_block(content, label):
    start = content.find(f'<label class="form-label">{label}')
    start = content.rfind('<div class="form-group">', 0, start)
    # Encontrar el cierre del div
    depth = 0
    i = start
    while i < len(content):
        if content[i:i+4] == '<div':
            depth += 1
        elif content[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                return start, i + 6, content[start:i+6]
        i += 1
    return -1, -1, ''

s1, e1, tipo_block = extract_block(content, 'Tipo de Guardia')
s2, e2, inicio_block = extract_block(content, 'Hora de Inicio')
s3, e3, fin_block = extract_block(content, 'Hora de Fin')
s4, e4, horas_block = extract_block(content, 'Horas Totales')

print('Bloques encontrados:', bool(tipo_block), bool(inicio_block), bool(fin_block), bool(horas_block))

# Reconstruir en el orden correcto: tipo, horas, inicio, fin
# Primero eliminar todos los bloques del contenido
# Encontrar donde empieza el primero y termina el ultimo
positions = sorted([(s1,e1,'tipo'), (s2,e2,'inicio'), (s3,e3,'fin'), (s4,e4,'horas')])
first_start = positions[0][0]
last_end = positions[-1][1]

new_blocks = '\n'.join([tipo_block, horas_block, inicio_block, fin_block])
content = content[:first_start] + new_blocks + content[last_end:]

with open('create.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Listo')
