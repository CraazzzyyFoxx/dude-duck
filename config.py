from pathlib import Path

from pydantic.v1 import BaseSettings


class Config(BaseSettings):
    TOKEN: str
    WEBHOOK_URL: str
    HOST: str
    PORT: int

    ADMIN_CHAT: int

    API_TOKEN: str
    SENTRY_DSN: str
    DEBUG: bool

    log_level: str = "info"
    logs_root_path: str = f"{Path.cwd()}/logs"

    class Config:
        env_file = ".env"
        env_prefix = "bot_"


app = Config()

BASE_DIR = Path(__file__).resolve().parent
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


START_MESSAGE: str = """
We glad to see you in our company. \n
Here is your welcome link for the orders conference: \n
<b>Dude Duck - Solo Orders | DF + WotLK</b> - https://t.me/+EFKRKNFJ2zw4ZDYy
<b>Dude Duck - Diablo 4 orders</b> - https://t.me/+ccshilMsCHwxZDA6
<b>Dude Duck - Solo Orders | DF + WotLK</b> - https://t.me/+EFKRKNFJ2zw4ZDYy
<b>Dude Duck - PvP Orders | DF + WotLK</b> - https://t.me/+aSioagb7zsExNjAy
<b>Dude Duck - M+/Dungeons Orders | DF + WotLK</b> - https://t.me/+qBd-GfONZu01Njky
<b>Dude Duck - Destiny 2 Orders</b> - https://t.me/+Yh0_rVJ1uF4yNDYy
<b>Dude Duck - EFT Orders</b> - https://t.me/+-46aQSCgtMI3NmU6
<b>Dude Duck - Mix Orders</b> - https://t.me/+jcEq2iOjlHxiM2Fi
"""
