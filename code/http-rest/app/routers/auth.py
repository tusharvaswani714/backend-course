import asyncio

from fastapi import APIRouter, Response

from app.config import settings
from app.errors import ApiError
from app.schemas import EmailIn, LoginIn, MessageOut, SignupIn, VerifyIn
from app.security import COOKIE_NAME, create_access_token, hash_password, verify_password
from app.store import UserRecord, database
from app.verification import check_code, issue_code

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=201, response_model=MessageOut)
async def signup(payload: SignupIn) -> MessageOut:
    password_hash = await asyncio.to_thread(hash_password, payload.password)
    if database.find_user_by_username(payload.username) is not None:
        raise ApiError(409, "conflict", "username is already taken")
    if database.find_user_by_email(payload.email) is not None:
        raise ApiError(409, "conflict", "email is already registered")
    database.users.append(
        UserRecord(
            id=len(database.users) + 1,
            username=payload.username,
            email=payload.email,
            password_hash=password_hash,
        )
    )
    issue_code(payload.email)
    return MessageOut(message="account created, check the console for your verification code")


@router.post("/verify", response_model=MessageOut)
async def verify(payload: VerifyIn) -> MessageOut:
    user = database.find_user_by_email(payload.email)
    if user is None or not check_code(payload.email, payload.code):
        raise ApiError(400, "invalid_code", "verification code is wrong or expired")
    user.verified = True
    return MessageOut(message="email verified")


@router.post("/resend-code", response_model=MessageOut)
async def resend_code(payload: EmailIn) -> MessageOut:
    user = database.find_user_by_email(payload.email)
    if user is not None and not user.verified:
        issue_code(payload.email)
    return MessageOut(message="if the account exists and is not verified, a new code was sent")


@router.post("/login", response_model=MessageOut)
async def login(payload: LoginIn, response: Response) -> MessageOut:
    user = database.find_user_by_username(payload.username)
    if user is None:
        raise ApiError(401, "invalid_credentials", "username or password is wrong")
    password_ok = await asyncio.to_thread(verify_password, payload.password, user.password_hash)
    if not password_ok:
        raise ApiError(401, "invalid_credentials", "username or password is wrong")
    if not user.verified:
        raise ApiError(403, "not_verified", "verify your email before logging in")
    response.set_cookie(
        key=COOKIE_NAME,
        value=create_access_token(user.username),
        max_age=settings.access_token_minutes * 60,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )
    return MessageOut(message="logged in")


@router.post("/logout", response_model=MessageOut)
async def logout(response: Response) -> MessageOut:
    response.delete_cookie(COOKIE_NAME, httponly=True, samesite="lax")
    return MessageOut(message="logged out")
