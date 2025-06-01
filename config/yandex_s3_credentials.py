from pydantic_settings import SettingsConfigDict

from config.base import ConfigBase


class YandexS3Credentials(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="yandex_s3_")

    ID_KEY: str
    SECRET_KEY: str
    ENDPOINT_URL: str
