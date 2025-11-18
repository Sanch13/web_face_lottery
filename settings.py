from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    DEBUG: bool
    ALLOWED_HOSTS: str

    TELEGRAM_API_TOKEN: str
    TELEGRAM_CHAT_ID: int

    DB_USER_PSQL: str
    DB_PASSWORD_PSQL: str
    DB_HOST_PSQL: str
    DB_PORT_PSQL: int
    DB_DATABASE_PSQL: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    SMTP_SERVER: str
    PORT: int
    SENDER_EMAIL: str
    PASSWORD: str
    ADMIN_EMAIL: str
    SUBJECT: str
    BODY: str
    TO_EMAIL: str
    TO_EMAILS: str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
