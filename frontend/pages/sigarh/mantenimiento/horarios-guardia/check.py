with open('create.vue', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('posterior')
print(repr(content[idx-150:idx+80]))
