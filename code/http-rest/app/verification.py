import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.config import settings
from app.errors import ApiError
from app.store import cache


def try_send(email: str) -> Optional[int]:
    now = datetime.now(timezone.utc)
    window = timedelta(minutes=settings.resend_window_minutes)
    recent = [sent for sent in cache.send_times.get(email, []) if now - sent < window]
    if len(recent) >= settings.resend_limit:
        cache.send_times[email] = recent
        retry_after = recent[0] + window - now
        return int(retry_after.total_seconds()) + 1
    recent.append(now)
    cache.send_times[email] = recent
    return None


def issue_code(email: str) -> None:
    retry_after = try_send(email)
    if retry_after is not None:
        raise ApiError(
            429,
            "rate_limited",
            "too many verification code requests, try again later",
            headers={"Retry-After": str(retry_after)},
        )
    code = f"{secrets.randbelow(1_000_000):06d}"
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.verification_code_minutes)
    cache.codes[email] = (code, expires)
    print(f"verification code for {email}: {code}")


def check_code(email: str, code: str) -> bool:
    entry = cache.codes.get(email)
    if entry is None:
        return False
    stored, expires = entry
    if datetime.now(timezone.utc) > expires or not secrets.compare_digest(stored, code):
        return False
    del cache.codes[email]
    return True
