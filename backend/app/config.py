from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    noise_enabled: bool = False
    max_shots: int = 4096
    default_shots: int = 1024
    default_noise: float = 0.01

    class Config:
        env_prefix = "BLOCH_"
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
