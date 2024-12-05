from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    DEBUG: bool

    DB_USER_PSQL: str
    DB_PASSWORD_PSQL: str
    DB_HOST_PSQL: str
    DB_PORT_PSQL: int
    DB_DATABASE_PSQL: str

    SMTP_SERVER: str
    PORT: int
    SENDER_EMAIL: str
    PASSWORD: str
    SUBJECT: str
    BODY: str
    TO_EMAIL: str
    TO_EMAILS: str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
