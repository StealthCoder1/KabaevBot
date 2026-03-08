import os
from pathlib import Path


def _load_env_file() -> None:
    """Load key=value pairs from the project .env into os.environ if missing."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _parse_admin_ids(raw_value: str) -> list[int]:
    parts = [part.strip() for part in raw_value.split(",") if part.strip()]
    return [int(part) for part in parts]


def _parse_bool(raw_value: str | None, default: bool = False) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


_load_env_file()


TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
DEBUG = _parse_bool(os.getenv("DEBUG"), False)
ADMIN_TG_ID = _parse_admin_ids(os.getenv("ADMIN_TG_ID", "7079975091,7875342185"))
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/kabaevbot?ssl=disable",
)
INTERVAL_MINUTES_FOR_SEND_DB = int(os.getenv("INTERVAL_MINUTES_FOR_SEND_DB", "30"))
