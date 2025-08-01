from sqlalchemy import Integer, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
     pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # noqa: A003
    login_name: Mapped[str] = mapped_column(String(32))
