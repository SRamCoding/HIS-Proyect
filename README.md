# ERP Hospitalario

Sistema ERP para gestión hospitalaria multi-tenant.

## Stack
- **Backend:** FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL 15
- **Frontend:** Nuxt 3 + Nuxt UI + Pinia
- **Infra:** Docker, Redis, RabbitMQ

## Levantar entorno de desarrollo

### Requisitos
- Docker Desktop
- Python 3.11+
- Node.js 20+

### Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp .env.example .env
# Editar .env con tus valores
```

### Infraestructura
```powershell
cd infra
docker compose up -d postgres redis rabbitmq
```

### Migraciones
```powershell
cd backend
alembic upgrade head
python -m app.auth.seeder
```

### Servidor
```powershell
uvicorn main:app --reload
```

API disponible en `http://localhost:8000/docs`