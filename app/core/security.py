import os
import time
import hmac
import json
import base64
import hashlib
from typing import Optional

# Read from .env if present (via python-dotenv loaded in config)
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-.env")
TOKEN_TTL_SECONDS = int(os.getenv("TOKEN_TTL_SECONDS", "3600"))  # 1 hour

# -----------------------
# Password hashing helpers
# -----------------------
def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("utf-8").rstrip("=")

def _b64d(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def hash_password(password: str) -> str:
    """
    Returns 'salt$hash' where:
      salt = 16 random bytes (base64url)
      hash = sha256(salt || password) (base64url)
    """
    if not isinstance(password, str):
        raise TypeError("password must be str")
    salt = os.urandom(16)
    digest = hashlib.sha256(salt + password.encode("utf-8")).digest()
    return f"{_b64e(salt)}${_b64e(digest)}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_b64, hash_b64 = stored.split("$", 1)
        salt = _b64d(salt_b64)
        expected = _b64d(hash_b64)
    except Exception:
        return False
    digest = hashlib.sha256(salt + password.encode("utf-8")).digest()
    return hmac.compare_digest(digest, expected)

# -----------------------
# Minimal signed tokens
# -----------------------
def create_token(subject: str, ttl_seconds: Optional[int] = None) -> str:
    """
    Creates a compact HMAC-SHA256 signed token.
    Payload: {"sub": subject, "exp": unix_ts}
    """
    ttl = ttl_seconds or TOKEN_TTL_SECONDS
    payload = {"sub": subject, "exp": int(time.time()) + ttl}
    payload_b = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sig = hmac.new(SECRET_KEY.encode("utf-8"), payload_b, hashlib.sha256).digest()
    return f"{_b64e(payload_b)}.{_b64e(sig)}"

def verify_token(token: str) -> Optional[dict]:
    """
    Verifies token integrity and expiration.
    Returns payload dict if valid, else None.
    """
    try:
        payload_b64, sig_b64 = token.split(".", 1)
        payload_b = _b64d(payload_b64)
        given_sig = _b64d(sig_b64)
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), payload_b, hashlib.sha256).digest()
        if not hmac.compare_digest(given_sig, expected_sig):
            return None
        data = json.loads(payload_b)
        if not isinstance(data, dict):
            return None
        if int(data.get("exp", 0)) < int(time.time()):
            return None
        return data
    except Exception:
        return None
