from app.security import build_line_signature, verify_line_signature


def test_verify_line_signature_accepts_valid_signature() -> None:
    body = b'{"destination":"Uxxx","events":[]}'
    secret = "test-secret"
    signature = build_line_signature(body, secret)

    assert verify_line_signature(body, signature, secret) is True


def test_verify_line_signature_rejects_invalid_signature() -> None:
    body = b'{"destination":"Uxxx","events":[]}'

    assert verify_line_signature(body, "invalid", "test-secret") is False
