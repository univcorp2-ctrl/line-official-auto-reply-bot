from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "line-official-auto-reply-bot"
    app_env: str = "development"

    line_channel_secret: str = "dev-secret"
    line_channel_access_token: str = ""
    line_api_base_url: str = "https://api.line.me"
    line_api_timeout_seconds: float = 10.0
    dry_run: bool = False

    reply_mode: Literal["rules", "ai", "hybrid"] = "rules"
    rules_path: str = "app/rules.yml"
    max_reply_chars: int = 900

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.5"
    openai_max_output_tokens: int = 350
    openai_system_prompt: str = (
        "あなたはLINE公式アカウントの一次対応担当です。"
        "短く、丁寧に、日本語で返信してください。"
        "予約、解約、個人情報、料金、クレームなど重要な内容は、"
        "必要に応じて担当者確認を案内してください。"
    )

    database_url: str = "sqlite:///./data/line_events.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
