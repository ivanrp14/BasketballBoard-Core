# db.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Cargar variables de entorno desde .env
load_dotenv()

# Inicializar conexión y crear tablas (opcional)
async def connect_postgres():
    async with engine.begin() as conn:
        # Solo crea tablas si no existen
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Conectado a PostgreSQL con SQLAlchemy async")
# Seleccionar URL según el modo
if os.getenv("MODE") == "development":
    DATABASE_URL = os.getenv("POSTGRES_URL_DEV")
else:
    DATABASE_URL = os.getenv("POSTGRES_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL no está configurada. Revisa tu archivo .env")

# Motor async
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Sesiones async
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Base de modelos
Base = declarative_base()




# db.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
