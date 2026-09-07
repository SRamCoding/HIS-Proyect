import json
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.shared.ubigeo.models import UbigeoDepartamento, UbigeoProvincia, UbigeoDistrito

DATA_DIR = Path(__file__).parent / "data"


async def seed_ubigeo(db: AsyncSession) -> None:
    departamentos = json.loads((DATA_DIR / "departamentos.json").read_text(encoding="utf-8"))
    provincias = json.loads((DATA_DIR / "provincias.json").read_text(encoding="utf-8"))
    distritos = json.loads((DATA_DIR / "distritos.json").read_text(encoding="utf-8"))

    for d in departamentos:
        db.add(UbigeoDepartamento(id=d["id"], nombre=d["name"]))
    await db.flush()

    for p in provincias:
        db.add(UbigeoProvincia(id=p["id"], departamento_id=p["department_id"], nombre=p["name"]))
    await db.flush()

    for dist in distritos:
        db.add(UbigeoDistrito(id=dist["id"], provincia_id=dist["province_id"], nombre=dist["name"]))

    await db.commit()
    print(f"Sembrados: {len(departamentos)} deptos, {len(provincias)} provincias, {len(distritos)} distritos")


if __name__ == "__main__":
    async def main():
        async with AsyncSessionLocal() as db:
            await seed_ubigeo(db)
    asyncio.run(main())