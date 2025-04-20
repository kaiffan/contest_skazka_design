from pydantic_settings import SettingsConfigDict

from config.base import ConfigBase


class PostgresCredentials(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="postgres_")

    DATABASE_NAME: str
    USERNAME: str
    PASSWORD: str
    HOST: str
    PORT: str
