from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class UserRecord:
    id: int
    username: str
    email: str
    password_hash: str
    verified: bool = False


@dataclass
class PostRecord:
    id: int
    author_id: int
    title: str
    body: str
    created_at: datetime


@dataclass
class Database:
    users: list[UserRecord] = field(default_factory=list)
    posts: list[PostRecord] = field(default_factory=list)
    next_post_id: int = 1

    def find_user_by_username(self, username: str) -> Optional[UserRecord]:
        for user in self.users:
            if user.username == username:
                return user
        return None

    def find_user_by_email(self, email: str) -> Optional[UserRecord]:
        for user in self.users:
            if user.email == email:
                return user
        return None

    def find_user_by_id(self, user_id: int) -> Optional[UserRecord]:
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def find_post(self, post_id: int) -> Optional[PostRecord]:
        for post in self.posts:
            if post.id == post_id:
                return post
        return None


@dataclass
class Cache:
    codes: dict[str, tuple[str, datetime]] = field(default_factory=dict)
    send_times: dict[str, list[datetime]] = field(default_factory=dict)


database = Database()
cache = Cache()
