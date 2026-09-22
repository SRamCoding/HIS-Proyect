import json
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.core.database import AsyncSessionLocal
from app.shared.ubigeo.models import UbigeoDepartamento, UbigeoProvincia, UbigeoDistrito

DATA_DIR = Path(__file__).parent / "data"


async def seed_ubigeo(db: AsyncSession) -> None:
    departamentos = json.loads((DATA_DIR / "departamentos.json").read_text(encoding="utf-8"))
    provincias = json.loads((DATA_DIR / "provincias.json").read_text(encoding="utf-8"))
    distritos = json.loads((DATA_DIR / "distritos.json").read_text(encoding="utf-8"))

    # Insert missing catalog entries without deleting or overwriting existing data.
    # Table inserts also allow running this utility without loading all ORM models.
    for model, rows in [
        (UbigeoDepartamento, [{"id": d["id"], "nombre": d["name"]} for d in departamentos]),
        (UbigeoProvincia, [{"id": p["id"], "departamento_id": p["department_id"], "nombre": p["name"]} for p in provincias]),
        (UbigeoDistrito, [{"id": d["id"], "provincia_id": d["province_id"], "nombre": d["name"]} for d in distritos]),
    ]:
        if rows:
            await db.execute(insert(model.__table__).values(rows).on_conflict_do_nothing(index_elements=["id"]))

    await db.commit()
    print(f"Sembrados: {len(departamentos)} deptos, {len(provincias)} provincias, {len(distritos)} distritos")


if __name__ == "__main__":
    async def main():
        async with AsyncSessionLocal() as db:
            await seed_ubigeo(db)
    asyncio.run(main())
