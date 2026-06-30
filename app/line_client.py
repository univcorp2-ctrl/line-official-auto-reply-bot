from typing import Any

import httpx

from app.config import Settings


class LineReplyError(RuntimeError):
    pass


async def send_reply_text(
    reply_token: str,
    text: str,
    settings: Settings,
) -> dict[str, Any]:
    if settings.dry_run:
        return {
            "dry_run": True,
            "reply_token_present": bool(reply_token),
            "text": text,
        }

    if not settings.line_channel_access_token:
        raise LineReplyError(
            "LINE_CHANNEL_ACCESS_TOKEN is required unless LINE_DRY_RUN=true."
        )

    url = f"{settings.line_api_base_url.rstrip('/')}/v2/bot/message/reply"
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}],
    }
    headers = {
        "Authorization": f"Bearer {settings.line_channel_access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=settings.line_api_timeout_seconds) as client:
        response = await client.post(url, json=payload, headers=headers)

    if response.status_code >= 400:
        raise LineReplyError(
            f"LINE Reply API failed: status={response.status_code} body={response.text}"
        )

    return {
        "dry_run": False,
        "status_code": response.status_code,
        "line_request_id": response.headers.get("x-line-request-id"),
    }
