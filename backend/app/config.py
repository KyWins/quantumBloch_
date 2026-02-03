from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BLOCH_", env_file=".env")

    # Simulation settings
    noise_enabled: bool = False
    max_shots: int = 4096
    default_shots: int = 1024
    default_noise: float = 0.01

    # CORS settings
    cors_origins: List[str] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]
    cors_allow_credentials: bool = False
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    cors_allow_headers: List[str] = ["Content-Type"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
