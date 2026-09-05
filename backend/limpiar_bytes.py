path = "app/admin/seeder_niveles.py"
with open(path, "rb") as f:
    content = f.read()

if b"\x00" in content:
    content_limpio = content.replace(b"\x00", b"")
    with open(path, "wb") as f:
        f.write(content_limpio)
    print("Bytes nulos eliminados correctamente")
else:
    print("El archivo no tenia bytes nulos")