from typing import AsyncIterator, Iterator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from settings import settings

# sync engine is always enabled
db_url = settings.sqlalchemy_database_uri
if ":memory:" in db_url:
    # must use StaticPool for in-memory SQLite database
    # in order for different connections to share the same data
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=False,
        poolclass=StaticPool,
    )
else:
    engine = create_engine(db_url, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def db_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


# async engine can be enabled by setting
if settings.async_orm:
    async_engine = create_async_engine(db_url, echo=False)
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine, autoflush=False, future=True
    )

    async def async_db_session() -> AsyncIterator[AsyncSession]:
        async with AsyncSessionLocal() as session:
            yield session
