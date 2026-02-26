from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import make_url
from sqlalchemy import inspect, text
from Data.config import DATABASE_URL
from db.models import Base

db_url = make_url(DATABASE_URL)
connect_args = {}

# asyncpg defaults to SSL negotiation ("prefer") for TCP connections.
# Local Docker Postgres usually has SSL disabled and resets the connection.
if (
    db_url.drivername == "postgresql+asyncpg"
    and db_url.host in {"127.0.0.1", "localhost", "::1"}
    and "ssl" not in db_url.query
    and "sslmode" not in db_url.query
):
    connect_args["ssl"] = False

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


def _ensure_users_table_compat(sync_conn) -> None:
    inspector = inspect(sync_conn)
    if "users" not in inspector.get_table_names():
        return

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "first_name" not in user_columns:
        sync_conn.execute(text("ALTER TABLE users ADD COLUMN first_name VARCHAR(255)"))
        user_columns.add("first_name")
    if "last_name" not in user_columns:
        sync_conn.execute(text("ALTER TABLE users ADD COLUMN last_name VARCHAR(255)"))
        user_columns.add("last_name")

    if {"id", "full_name", "first_name", "last_name"}.issubset(user_columns):
        rows = sync_conn.execute(
            text("SELECT id, full_name, first_name, last_name FROM users")
        ).mappings().all()
        for row in rows:
            full_name = (row.get("full_name") or "").strip()
            if not full_name:
                continue

            current_first = (row.get("first_name") or "").strip()
            current_last = (row.get("last_name") or "").strip()
            if current_first and current_last:
                continue

            parts = full_name.split(maxsplit=1)
            inferred_first = parts[0] if parts else None
            inferred_last = parts[1] if len(parts) > 1 else None
            if not inferred_first and not inferred_last:
                continue

            sync_conn.execute(
                text(
                    """
                    UPDATE users
                    SET first_name = CASE
                        WHEN first_name IS NULL OR TRIM(first_name) = '' THEN :first_name
                        ELSE first_name
                    END,
                    last_name = CASE
                        WHEN last_name IS NULL OR TRIM(last_name) = '' THEN :last_name
                        ELSE last_name
                    END
                    WHERE id = :user_id
                    """
                ),
                {
                    "first_name": inferred_first,
                    "last_name": inferred_last,
                    "user_id": row["id"],
                },
            )

    # Remove legacy duplicate columns from users (best effort).
    # Works on PostgreSQL and modern SQLite; if unsupported, we keep columns in DB
    # but they are no longer used by the application model.
    for legacy_column in ("telegram_tag", "full_name"):
        if legacy_column not in user_columns:
            continue
        try:
            sync_conn.execute(text(f"ALTER TABLE users DROP COLUMN {legacy_column}"))
        except Exception:
            pass


async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_ensure_users_table_compat)

# Для запуска миграции (создания таблиц) использовать:
# asyncio.run(create_all_tables())

