import pytest

from helper import sync2async_database_url, is_in_memory_db


def test_async_db_url():
    assert (
        "postgresql+psycopg_async://user:pass@server/db?x=1&y=2"
        == sync2async_database_url("postgresql+psycopg://user:pass@server/db?x=1&y=2")
    )
    assert "postgresql+psycopg_async://@/db" == sync2async_database_url(
        "postgresql+psycopg://@/db"
    )

    assert "sqlite+aiosqlite:///tmp/app.db" == sync2async_database_url(
        "sqlite:///tmp/app.db"
    )
    assert "sqlite+aiosqlite://" == sync2async_database_url("sqlite://")
    assert "sqlite+aiosqlite:///:memory:" == sync2async_database_url(
        "sqlite:///:memory:"
    )

    assert (
        "mysql+aiomysql://user:pass@server/db?encoding=utf8"
        == sync2async_database_url("mysql+mysqldb://user:pass@server/db?encoding=utf8")
    )

    with pytest.raises(RuntimeError):
        assert "future+server://xyz.w" == sync2async_database_url(
            "future+server://xyz.w"
        )

def test_is_in_memory_db():
    assert is_in_memory_db("sqlite://")
    assert is_in_memory_db("sqlite:///:memory:")