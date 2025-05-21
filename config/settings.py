from config.email_credentials import EmailCredentials
from config.postgres_credentials import PostgresCredentials
from config.token_credentials import TokenCredentials
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    postgres_credentials: PostgresCredentials = Field(
        default_factory=PostgresCredentials
    )
    token_credentials: TokenCredentials = Field(default_factory=TokenCredentials)
    email_credentials: EmailCredentials = Field(default_factory=EmailCredentials)


@lru_cache
def get_settings() -> Settings:
    return Settings()
