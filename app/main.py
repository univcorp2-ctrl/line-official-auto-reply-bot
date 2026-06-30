import json
from json import JSONDecodeError
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request

from app.config import Settings, get_settings
from app.line_client import LineReplyError, send_reply_text
from app.responder import generate_reply, get_welcome_reply
from app.security import verify_line_signature
from app.storage import initialize_storage, record_event


def _source_id(event: dict[str, Any]) -> str | None:
    source = event.get("source", {})
    return source.get("userId") or source.get("groupId") or source.get("roomId")


async def process_event(event: dict[str, Any], settings: Settings) -> dict[str, Any]:
    event_type = str(event.get("type", "unknown"))
    source_id = _source_id(event)
    reply_token = event.get("replyToken")
    reply = None
    message_text = None
    delivery: dict[str, Any] | None = None

    if event_type == "message":
        message = event.get("message", {})
        message_type = message.get("type")
        if message_type == "text":
            message_text = str(message.get("text", ""))
            reply = await generate_reply(message_text, settings, event)
        else:
            reply = "ありがとうございます。現在はテキストメッセージに対応しています。"
    elif event_type == "follow":
        reply = get_welcome_reply(settings)
    else:
        record_event(settings, event_type, source_id, None, None, event)
        return {"event_type": event_type, "handled": False, "reason": "unsupported_event"}

    if reply and reply_token:
        delivery = await send_reply_text(str(reply_token), reply, settings)

    record_event(settings, event_type, source_id, message_text, reply, event)
    return {
        "event_type": event_type,
        "handled": True,
        "reply": bool(reply),
        "delivery": delivery,
    }


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(
        title="LINE Official Auto Reply Bot",
        description="Webhook receiver and auto-reply bot for LINE Official Account.",
        version="0.1.0",
    )
    app.state.settings = app_settings

    @app.on_event("startup")
    async def startup() -> None:
        initialize_storage(app_settings)

    @app.get("/healthz")
    async def healthz() -> dict[str, Any]:
        return {
            "ok": True,
            "service": app_settings.app_name,
            "env": app_settings.app_env,
            "reply_mode": app_settings.reply_mode,
            "dry_run": app_settings.dry_run,
        }

    @app.post("/webhook")
    async def webhook(
        request: Request,
        x_line_signature: str | None = Header(default=None, alias="x-line-signature"),
    ) -> dict[str, Any]:
        body = await request.body()
        if not verify_line_signature(
            body,
            x_line_signature,
            app_settings.line_channel_secret,
        ):
            raise HTTPException(status_code=400, detail="invalid line signature")

        try:
            payload = json.loads(body.decode("utf-8"))
        except JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="invalid json") from exc

        results = []
        for event in payload.get("events", []):
            try:
                results.append(await process_event(event, app_settings))
            except LineReplyError as exc:
                raise HTTPException(status_code=502, detail=str(exc)) from exc

        return {"ok": True, "processed": len(results), "results": results}

    return app


app = create_app()
