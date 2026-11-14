from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SignupIn(BaseModel):
    username: str = Field(pattern=r"^[a-zA-Z0-9_]{3,20}$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class EmailIn(BaseModel):
    email: EmailStr


class VerifyIn(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^[0-9]{6}$")


class LoginIn(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class MessageOut(BaseModel):
    message: str


class PublicUserOut(BaseModel):
    id: int
    username: str


class MeOut(BaseModel):
    id: int
    username: str
    email: str
    verified: bool


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1, max_length=2000)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    body: Optional[str] = Field(default=None, min_length=1, max_length=2000)


class PostOut(BaseModel):
    id: int
    title: str
    body: str
    author: str
    created_at: datetime


class PostPage(BaseModel):
    items: list[PostOut]
    total: int
    limit: int
    offset: int


class CursorPage(BaseModel):
    items: list[PostOut]
    next_cursor: Optional[int]
