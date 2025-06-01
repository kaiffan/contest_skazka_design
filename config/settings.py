from config.email_credentials import EmailCredentials
from config.postgres_credentials import PostgresCredentials
from config.token_credentials import TokenCredentials
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field

from config.vk_credentials import VkCredentials
from config.yandex_s3_credentials import YandexS3Credentials


class Settings(BaseSettings):
    postgres_credentials: PostgresCredentials = Field(
        default_factory=PostgresCredentials
    )
    yandex_s3_credentials: YandexS3Credentials = Field(
        default_factory=YandexS3Credentials
    )
    token_credentials: TokenCredentials = Field(default_factory=TokenCredentials)
    email_credentials: EmailCredentials = Field(default_factory=EmailCredentials)
    vk_credentials: VkCredentials = Field(default_factory=VkCredentials)


@lru_cache
def get_settings() -> Settings:
    return Settings()
