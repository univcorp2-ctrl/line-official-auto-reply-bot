# AI Agent Notes

## Project goal

Maintain a production-ready FastAPI bot for LINE Official Account auto replies.

## Commands

```bash
pip install -r requirements.txt
ruff check .
pytest -q
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Safety rules

- Never commit `.env` or real LINE/OpenAI secrets.
- Keep LINE webhook signature verification before JSON processing decisions.
- Keep tests for signature verification and webhook dry-run behavior.
- Prefer small, explicit integrations over hidden framework magic.

## Important files

- `app/main.py`: FastAPI routes and event processing
- `app/security.py`: LINE signature verification
- `app/line_client.py`: LINE Reply API client
- `app/responder.py`: rule and AI reply orchestration
- `app/rules.yml`: editable reply rules
