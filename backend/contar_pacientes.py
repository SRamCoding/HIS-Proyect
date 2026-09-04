import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT COUNT(*) FROM patients"))
        count = result.scalar()
        print(f"Total de pacientes en la tabla: {count}")


if __name__ == "__main__":
    asyncio.run(main())