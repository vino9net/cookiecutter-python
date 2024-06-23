import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

__all__ = ["SessionLocal", "engine"]

load_dotenv()

db_url = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///memory:")

#
# begin of sync db setup, remove and uncomment async setup below if needed
#
conn_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

db_url = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///memory:")
engine = create_engine(db_url, connect_args=conn_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#
# begin of async db setup, uncomment and remove sync setup above if needed
#
# db_url = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite+aiosqlite:///memory:")
# engine = create_async_engine(db_url, echo=False)
# SessionLocal = async_sessionmaker(bind=engine, autoflush=False, future=True)
