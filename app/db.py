from typing import AsyncGenerator
import os
import logging
from pathlib import Path

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configurar banco de dados
DB_PATH = Path(__file__).parent.parent / "test.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH.absolute()}"
logger.info(f"Using database at: {DATABASE_URL}")


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)


# Criar engine com echo=True para logs SQL
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    try:
        logger.info("Creating database and tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database and tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_session_maker() as session:
            logger.debug("Created new database session")
            yield session
            logger.debug("Database session closed")
    except Exception as e:
        logger.error(f"Error in database session: {e}")
        raise


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    try:
        yield SQLAlchemyUserDatabase(session, User)
    except Exception as e:
        logger.error(f"Error in user database: {e}")
        raise 