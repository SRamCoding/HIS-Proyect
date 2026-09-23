import base64
from io import BytesIO
import pytest
from PIL import Image
from pydantic import ValidationError
from app.tenants.hospitales.branding import normalizar_logo, MAX_LOGO_BYTES
from app.tenants.hospitales.schemas import TenantUpdate


def image_data(fmt="PNG", size=(1200, 600)):
    output = BytesIO()
    Image.new("RGB", size, "#287953").save(output, format=fmt)
    mime = {"PNG": "png", "JPEG": "jpeg", "WEBP": "webp"}[fmt]
    return f"data:image/{mime};base64," + base64.b64encode(output.getvalue()).decode()


@pytest.mark.parametrize("fmt", ["PNG", "JPEG", "WEBP"])
def test_logo_se_normaliza_y_conserva_proporcion(fmt):
    result = normalizar_logo(image_data(fmt))
    assert result.startswith("data:image/png;base64,")
    with Image.open(BytesIO(base64.b64decode(result.split(",")[1]))) as image:
        assert image.size == (768, 384)
        assert not image.getexif()
    assert normalizar_logo(result) == result


@pytest.mark.parametrize("data", ["https://example.com/logo.png", "data:image/svg+xml;base64,PHN2Zz4=", "data:image/png;base64,bm8=", "data:image/png;base64,%%%"])
def test_logo_rechaza_urls_svg_y_contenido_invalido(data):
    with pytest.raises(ValueError):
        normalizar_logo(data)


def test_limite_y_tipo_real():
    with pytest.raises(ValueError):
        normalizar_logo("data:image/png;base64," + "A" * (MAX_LOGO_BYTES * 2))
    with pytest.raises(ValueError):
        normalizar_logo(image_data("JPEG").replace("image/jpeg", "image/png"))
    with pytest.raises(ValueError):
        normalizar_logo(image_data(size=(4100, 4000)))


def test_patch_distingue_omitir_y_quitar_logo():
    assert "logo_url" not in TenantUpdate(name="Hospital nuevo").model_dump(exclude_unset=True)
    assert TenantUpdate(logo_url=None).model_dump(exclude_unset=True) == {"logo_url": None}
    assert TenantUpdate(logo_url=image_data()).logo_url == normalizar_logo(image_data())
    with pytest.raises(ValidationError):
        TenantUpdate(logo_url="javascript:alert(1)")
