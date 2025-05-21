from pydantic_settings import SettingsConfigDict

from config.base import ConfigBase


class EmailCredentials(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="EMAIL_")

    HOST: str
    PORT: int
    HOST_USER: str
    HOST_PASSWORD: str
