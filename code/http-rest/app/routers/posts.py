from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query, Request, Response

from app.auth_middleware import current_user
from app.errors import ApiError
from app.schemas import CursorPage, PostCreate, PostOut, PostPage, PostUpdate
from app.store import PostRecord, UserRecord, database

router = APIRouter(prefix="/posts", tags=["posts"])


def to_post_out(post: PostRecord) -> PostOut:
    author = database.find_user_by_id(post.author_id)
    username = author.username if author is not None else "unknown"
    return PostOut(
        id=post.id,
        title=post.title,
        body=post.body,
        author=username,
        created_at=post.created_at,
    )


def load_owned_post(post_id: int, user: UserRecord) -> PostRecord:
    post = database.find_post(post_id)
    if post is None:
        raise ApiError(404, "not_found", "post does not exist")
    if post.author_id != user.id:
        raise ApiError(403, "forbidden", "you can only change your own posts")
    return post


@router.post("", status_code=201, response_model=PostOut)
async def create_post(payload: PostCreate, request: Request) -> PostOut:
    user = current_user(request)
    post = PostRecord(
        id=database.next_post_id,
        author_id=user.id,
        title=payload.title,
        body=payload.body,
        created_at=datetime.now(timezone.utc),
    )
    database.next_post_id += 1
    database.posts.insert(0, post)
    return to_post_out(post)


@router.get("", response_model=PostPage)
async def list_posts(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PostPage:
    selected = database.posts[offset : offset + limit]
    return PostPage(
        items=[to_post_out(post) for post in selected],
        total=len(database.posts),
        limit=limit,
        offset=offset,
    )


@router.get("/cursor", response_model=CursorPage)
async def list_posts_by_cursor(
    limit: int = Query(default=10, ge=1, le=100),
    cursor: Optional[int] = Query(default=None, ge=1),
) -> CursorPage:
    candidates = [post for post in database.posts if cursor is None or post.id < cursor]
    page = candidates[:limit]
    next_cursor = page[-1].id if len(candidates) > limit else None
    return CursorPage(items=[to_post_out(post) for post in page], next_cursor=next_cursor)


@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: int) -> PostOut:
    post = database.find_post(post_id)
    if post is None:
        raise ApiError(404, "not_found", "post does not exist")
    return to_post_out(post)


@router.patch("/{post_id}", response_model=PostOut)
async def update_post(post_id: int, payload: PostUpdate, request: Request) -> PostOut:
    post = load_owned_post(post_id, current_user(request))
    if payload.title is not None:
        post.title = payload.title
    if payload.body is not None:
        post.body = payload.body
    return to_post_out(post)


@router.delete("/{post_id}", status_code=204, response_class=Response)
async def delete_post(post_id: int, request: Request) -> Response:
    post = load_owned_post(post_id, current_user(request))
    database.posts.remove(post)
    return Response(status_code=204)
