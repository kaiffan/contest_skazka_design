from os import path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=path.abspath(path=path.join(path.dirname(__file__), "../.env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )
