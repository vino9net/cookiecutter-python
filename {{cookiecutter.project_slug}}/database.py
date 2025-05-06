from typing import AsyncIterator, Iterator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from settings import settings


def _is_in_memory_db(db_url: str) -> bool:
    """
    check if the database is an in-memory SQLite database
    """
    return db_url in [
        "sqlite://",
        "sqlite:///:memory:",
        "sqlite+aiosqlite://",
        "sqlite+aiosqlite:///:memory:",
    ]


echo = settings.enable_sqlalchemy_echo

# sync engine is always enabled
db_url = settings.database_url
if _is_in_memory_db(db_url):
    # must use StaticPool for in-memory SQLite database
    # in order for different connections to share the same data
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=echo,
        poolclass=StaticPool,
    )
else:
    engine = create_engine(db_url, echo=echo)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def db_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


# async engine can be enabled by setting
if settings.async_orm:
    db_url_async = settings.database_url_async
    if _is_in_memory_db(db_url_async):
        async_engine = create_async_engine(
            db_url_async,
            connect_args={"check_same_thread": False},
            echo=echo,
            poolclass=StaticPool,
        )
    else:
        async_engine = create_async_engine(db_url_async, echo=echo)

    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine, autoflush=False, future=True
    )

    async def async_db_session() -> AsyncIterator[AsyncSession]:
        async with AsyncSessionLocal() as session:
            yield session
