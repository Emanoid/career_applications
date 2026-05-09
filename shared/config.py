import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class _EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    firebase_credentials_json: str = ""
    firebase_web_api_key: str = ""


class Settings:
    def __init__(self, credentials_json: str, web_api_key: str) -> None:
        self.firebase_credentials_json = credentials_json
        self.firebase_web_api_key = web_api_key


@lru_cache(maxsize=1)
def _env_settings() -> _EnvSettings:
    return _EnvSettings()


def get_settings() -> Settings:
    """Load config from Streamlit secrets (prod) with env-var fallback (CI/local)."""
    env = _env_settings()
    credentials_json = env.firebase_credentials_json
    web_api_key = env.firebase_web_api_key

    if not credentials_json or not web_api_key:
        try:
            import streamlit as st

            fb = st.secrets.get("firebase", {})
            credentials_json = credentials_json or fb.get("credentials_json", "")
            web_api_key = web_api_key or fb.get("web_api_key", "")
        except Exception:
            pass

    return Settings(credentials_json=credentials_json, web_api_key=web_api_key)
