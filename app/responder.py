from pathlib import Path
from typing import Any

import yaml

from app.ai_client import generate_ai_reply
from app.config import Settings

DEFAULT_RULES: dict[str, Any] = {
    "welcome_reply": "友だち追加ありがとうございます。ご用件をメッセージでお送りください。",
    "default_reply": "お問い合わせありがとうございます。内容を確認しました。担当者が必要な場合は順次対応します。",
    "handoff_reply": "お問い合わせありがとうございます。この内容は担当者が確認して対応します。少々お待ちください。",
    "handoff_keywords": ["担当者", "人に代わって", "クレーム", "解約", "返金"],
    "keywords": [],
}


def load_rules(path: str) -> dict[str, Any]:
    rules_path = Path(path)
    if not rules_path.exists():
        return DEFAULT_RULES.copy()

    with rules_path.open("r", encoding="utf-8") as file:
        loaded = yaml.safe_load(file) or {}

    merged = DEFAULT_RULES.copy()
    merged.update(loaded)
    return merged


def _contains(text: str, keyword: str) -> bool:
    return keyword.casefold() in text.casefold()


def _clip(text: str, max_chars: int) -> str:
    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 1] + "…"


def get_welcome_reply(settings: Settings) -> str:
    rules = load_rules(settings.rules_path)
    return _clip(str(rules.get("welcome_reply")), settings.max_reply_chars)


async def generate_reply(
    user_text: str,
    settings: Settings,
    event: dict[str, Any] | None = None,
) -> str:
    del event
    rules = load_rules(settings.rules_path)
    text = user_text.strip()

    if not text:
        return _clip(str(rules.get("default_reply")), settings.max_reply_chars)

    for keyword in rules.get("handoff_keywords", []):
        if _contains(text, str(keyword)):
            return _clip(str(rules.get("handoff_reply")), settings.max_reply_chars)

    for rule in rules.get("keywords", []):
        contains = str(rule.get("contains", ""))
        reply = rule.get("reply")
        if contains and reply and _contains(text, contains):
            return _clip(str(reply), settings.max_reply_chars)

    if settings.reply_mode in {"ai", "hybrid"}:
        ai_reply = await generate_ai_reply(text, settings)
        if ai_reply:
            return _clip(ai_reply, settings.max_reply_chars)

    return _clip(str(rules.get("default_reply")), settings.max_reply_chars)
