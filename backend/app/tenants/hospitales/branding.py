"""Logos institucionales normalizados; sin URLs remotas ni SVG."""
import base64
import binascii
from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_LOGO_BYTES = 2 * 1024 * 1024


def normalizar_logo(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) > MAX_LOGO_BYTES * 4 // 3 + 128:
        raise ValueError("El logo no puede superar 2 MB")
    prefix, sep, payload = value.partition(",")
    formats = {"data:image/png;base64": "PNG", "data:image/jpeg;base64": "JPEG", "data:image/webp;base64": "WEBP"}
    if not sep or prefix not in formats:
        raise ValueError("Selecciona un logo PNG, JPG o WebP")
    try:
        raw = base64.b64decode(payload, validate=True)
        if len(raw) > MAX_LOGO_BYTES:
            raise ValueError("El logo no puede superar 2 MB")
        with Image.open(BytesIO(raw)) as source:
            if source.format != formats[prefix] or source.width * source.height > 16_000_000:
                raise ValueError("Formato o dimensiones del logo no válidos")
            source.load()
            img = ImageOps.exif_transpose(source).convert("RGBA")
            img.thumbnail((768, 768), Image.Resampling.LANCZOS)
            output = BytesIO()
            img.save(output, format="PNG", optimize=True)
            return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii")
    except (UnidentifiedImageError, OSError, binascii.Error, Image.DecompressionBombError) as exc:
        raise ValueError("El archivo no es una imagen válida") from exc
