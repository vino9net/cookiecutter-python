from urllib.parse import urlparse, urlunparse

def is_in_memory_db(db_url: str) -> bool:
    """
    check if the database is an in-memory SQLite database
    """
    return db_url in [
        "sqlite://",
        "sqlite:///:memory:",
        "sqlite+aiosqlite://",
        "sqlite+aiosqlite:///:memory:",
    ]

def sync2async_database_url(db_url: str) -> str:
    """
    derive async database URL from sync database URL
    """
    if db_url.startswith("sqlite://"):
        return db_url.replace("sqlite://", "sqlite+aiosqlite://")

    parsed = urlparse(db_url)
    parts = parsed.scheme.split("+")
    db_type, driver = parts[0], parts[1] if len(parts) > 1 else ""

    if db_type == "postgresql":
        driver = "psycopg_async"
    elif db_type == "mysql":
        driver = "aiomysql"
    else:
        # for unsupported database types, we just return the original URL
        raise RuntimeError("Unsupported database type {database_url}")

    return urlunparse(parsed._replace(scheme=f"{db_type}+{driver}"))
