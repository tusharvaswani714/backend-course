from fastapi import APIRouter, Query, Request

from app.auth_middleware import current_user
from app.errors import ApiError
from app.routers.posts import to_post_out
from app.schemas import MeOut, PostPage, PublicUserOut
from app.store import database

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=MeOut)
async def get_me(request: Request) -> MeOut:
    user = current_user(request)
    return MeOut(id=user.id, username=user.username, email=user.email, verified=user.verified)


@router.get("/{username}", response_model=PublicUserOut)
async def get_user(username: str) -> PublicUserOut:
    user = database.find_user_by_username(username)
    if user is None:
        raise ApiError(404, "not_found", "user does not exist")
    return PublicUserOut(id=user.id, username=user.username)


@router.get("/{username}/posts", response_model=PostPage)
async def get_user_posts(
    username: str,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PostPage:
    user = database.find_user_by_username(username)
    if user is None:
        raise ApiError(404, "not_found", "user does not exist")
    authored = [post for post in database.posts if post.author_id == user.id]
    selected = authored[offset : offset + limit]
    return PostPage(
        items=[to_post_out(post) for post in selected],
        total=len(authored),
        limit=limit,
        offset=offset,
    )
