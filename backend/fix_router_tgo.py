with open('app/sigarh/mantenimiento/router.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'make_crud(router, "tipos-grupo-ocupacional", TipoGrupoOcupacionalCreate, TipoGrupoOcupacionalResponse, "sigarh_mantenimiento")\n\n',
    ''
)
content = content.replace(
    'make_crud(router, "tipos-grupo-ocupacional", TipoGrupoOcupacionalCreate, TipoGrupoOcupacionalResponse, "sigarh_mantenimiento")\n',
    ''
)

with open('app/sigarh/mantenimiento/router.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Listo')
