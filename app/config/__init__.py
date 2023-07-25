from pathlib import Path

from pydantic.v1 import BaseSettings


class Config(BaseSettings):
    token: str
    webhook_url: str
    host: str
    port: int

    admin_chat: int

    api_token: str
    api_token_bot: str
    sentry_dsn: str
    debug: bool

    log_level: str = "info"
    logs_root_path: str = f"{Path.cwd()}/logs"

    class Config:
        env_file = ".env"
        env_prefix = "bot_"


BASE_DIR = Path(__file__).resolve().parent.parent.parent
SQLITE_DB_FILE = BASE_DIR / "db"
SQLITE_DB_FILE.mkdir(exist_ok=True)
SQLITE_DB_FILE = BASE_DIR / "db" / "db.sqlite3"
GOOGLE_CONFIG_FILE = BASE_DIR / "google.json"


tortoise = {
    "connections": {
        "default": f"sqlite://{SQLITE_DB_FILE}", },

    "apps": {
        "main": {
            "models": ["app.db", "aerich.models"],
            "default_connection": "default",
        }
    },
}
