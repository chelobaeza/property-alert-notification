from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from property_alert_notification.core.config import settings

engine = create_async_engine(str(settings.DATABASE_URL), connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db(session: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    
    from sqlmodel import SQLModel
    # SQLModel.metadata.create_all(engine)
    
    async with session.bind.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    # async with engine.begin() as conn:
    #     await conn.run_sync(SQLModel.metadata.create_all)
