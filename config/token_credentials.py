from pydantic_settings import SettingsConfigDict

from config.base import ConfigBase


class TokenCredentials(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="TOKEN_")

    REFRESH_COOKIE_KEY: str
    REFRESH_COOKIE_PATH: str
    REFRESH_COOKIE_MAX_AGE: int
    SECRET_KEY: str
