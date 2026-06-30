import json

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.security import build_line_signature


def _signed_body(payload: dict, secret: str) -> tuple[bytes, str]:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return body, build_line_signature(body, secret)


def test_line_webhook_processes_text_message_in_dry_run(tmp_path) -> None:
    settings = Settings(
        line_channel_secret="test-secret",
        line_channel_access_token="",
        dry_run=True,
        database_url=f"sqlite:///{tmp_path / 'events.db'}",
    )
    client = TestClient(create_app(settings))
    payload = {
        "destination": "Udestination",
        "events": [
            {
                "type": "message",
                "replyToken": "reply-token",
                "source": {"type": "user", "userId": "Uuser"},
                "timestamp": 1700000000000,
                "mode": "active",
                "message": {"id": "1", "type": "text", "text": "営業時間を教えて"},
            }
        ],
    }
    body, signature = _signed_body(payload, settings.line_channel_secret)

    response = client.post(
        "/webhook",
        data=body,
        headers={"content-type": "application/json", "x-line-signature": signature},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["processed"] == 1
    assert data["results"][0]["handled"] is True
    assert data["results"][0]["delivery"]["dry_run"] is True


def test_line_webhook_rejects_invalid_signature(tmp_path) -> None:
    settings = Settings(
        line_channel_secret="test-secret",
        dry_run=True,
        database_url=f"sqlite:///{tmp_path / 'events.db'}",
    )
    client = TestClient(create_app(settings))
    payload = {"destination": "Udestination", "events": []}
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    response = client.post(
        "/webhook",
        data=body,
        headers={"content-type": "application/json", "x-line-signature": "invalid"},
    )

    assert response.status_code == 400
