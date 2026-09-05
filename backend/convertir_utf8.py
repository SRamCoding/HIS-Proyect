path = "app/admin/seeder_niveles.py"

with open(path, "rb") as f:
    raw = f.read()

# Detecta y remueve BOM de UTF-16 (LE o BE), luego decodifica y re-guarda en UTF-8 limpio
if raw.startswith(b"\xff\xfe"):
    texto = raw.decode("utf-16-le")
elif raw.startswith(b"\xfe\xff"):
    texto = raw.decode("utf-16-be")
elif raw.startswith(b"\xef\xbb\xbf"):
    texto = raw.decode("utf-8-sig")
else:
    texto = raw.decode("utf-8")

with open(path, "w", encoding="utf-8") as f:
    f.write(texto)

print("Archivo reescrito en UTF-8 limpio, sin BOM")