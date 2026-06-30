import asyncio

from app.config import Settings
from app.responder import generate_reply


def test_rule_based_reply_matches_keyword(tmp_path) -> None:
    rules_path = tmp_path / "rules.yml"
    rules_path.write_text(
        "default_reply: デフォルト返信\n"
        "keywords:\n"
        "  - contains: 営業時間\n"
        "    reply: 営業時間は10時からです。\n",
        encoding="utf-8",
    )
    settings = Settings(rules_path=str(rules_path), reply_mode="rules")

    reply = asyncio.run(generate_reply("営業時間を教えてください", settings))

    assert reply == "営業時間は10時からです。"


def test_default_reply_is_used_when_no_keyword_matches(tmp_path) -> None:
    rules_path = tmp_path / "rules.yml"
    rules_path.write_text("default_reply: 受け付けました。\nkeywords: []\n", encoding="utf-8")
    settings = Settings(rules_path=str(rules_path), reply_mode="rules")

    reply = asyncio.run(generate_reply("こんにちは", settings))

    assert reply == "受け付けました。"
