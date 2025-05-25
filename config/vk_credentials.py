from pydantic_settings import SettingsConfigDict

from config.base import ConfigBase


class VkCredentials(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="vk_")

    TOKEN: str
    DOMAIN: str
