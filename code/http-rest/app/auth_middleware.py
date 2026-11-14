from typing import Awaitable, Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.errors import ApiError, error_body
from app.security import COOKIE_NAME, read_access_token
from app.store import UserRecord, database

WRITE_METHODS = {"POST", "PATCH", "DELETE"}


def requires_login(request: Request) -> bool:
    path = request.url.path
    if path == "/users/me":
        return True
    return path.startswith("/posts") and request.method in WRITE_METHODS


def find_session_user(request: Request) -> Optional[UserRecord]:
    token = request.cookies.get(COOKIE_NAME)
    if token is None:
        return None
    username = read_access_token(token)
    if username is None:
        return None
    return database.find_user_by_username(username)


async def authenticate(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    user = find_session_user(request)
    request.state.user = user
    if requires_login(request):
        if user is None:
            return JSONResponse(status_code=401, content=error_body("unauthorized", "log in first"))
        if not user.verified:
            return JSONResponse(status_code=403, content=error_body("not_verified", "verify your email first"))
    return await call_next(request)


def current_user(request: Request) -> UserRecord:
    user = getattr(request.state, "user", None)
    if not isinstance(user, UserRecord):
        raise ApiError(401, "unauthorized", "log in first")
    return user
