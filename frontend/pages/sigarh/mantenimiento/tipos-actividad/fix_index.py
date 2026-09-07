import re

with open('index.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Eliminar th de descripcion
content = re.sub(r'\s*<th class="col-description">\s*<span class="th-content">Descripci[^<]*</span>\s*</th>', '', content)

# Eliminar td de descripcion
content = re.sub(r'\s*<td class="col-description">[^<]*</td>', '', content)

# Eliminar CSS col-description y description-text
content = re.sub(r'\.col-description \{[^}]*\}', '', content)
content = re.sub(r'/\* Description \*/\s*\.description-text \{[^}]*\}', '', content)
content = re.sub(r'\.description-text \{[^}]*\}', '', content)

with open('index.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Listo')
