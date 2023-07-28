from pathlib import Path

from pydantic_settings import SettingsConfigDict, BaseSettings


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='app_', env_file=".env", env_file_encoding='utf-8')

    bot_token: str
    bot_webhook_url: str
    bot_api_token: str

    host: str
    port: int

    admin_chat: int

    api_token: str
    sentry_dsn: str
    debug: bool

    secret: str
    algorithm: str = 'HS256'
    expires_s: int = 3600

    log_level: str = "info"
    logs_root_path: str = f"{Path.cwd()}/logs"


app = AppConfig(_env_file='.env', _env_file_encoding='utf-8')


BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
GOOGLE_CONFIG_FILE = BASE_DIR / "google.json"
