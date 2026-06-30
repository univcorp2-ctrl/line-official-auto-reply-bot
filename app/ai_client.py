from app.config import Settings


def _clean_text(text: str, max_chars: int) -> str:
    cleaned = " ".join(text.strip().split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 1] + "…"


async def generate_ai_reply(user_text: str, settings: Settings) -> str | None:
    if not settings.openai_api_key:
        return None

    try:
        from openai import AsyncOpenAI
    except ImportError:
        return None

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    try:
        response = await client.responses.create(
            model=settings.openai_model,
            instructions=settings.openai_system_prompt,
            input=user_text,
            max_output_tokens=settings.openai_max_output_tokens,
        )
    except Exception:
        return None

    output_text = getattr(response, "output_text", None)
    if output_text:
        return _clean_text(output_text, settings.max_reply_chars)

    return None
