from typing import Type
import inject
from fastapi import APIRouter, Response, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from hex.domain.actions.get_post import GetPost, PostNotFound
from hex.domain.actions.search_posts import SearchPosts
from hex.web.responses import create_error_response
from hex.web.error_handlers import ErrorHandlers


@inject.autoparams()
def create_post_router(search_posts: SearchPosts, get_post: GetPost) -> APIRouter:
    post_router = APIRouter(
        prefix="/posts",
        tags=["posts"],
        # dependencies=[Depends(get_token_header)],
        responses={404: {"description": "Not found"}},
    )

    @post_router.get('/')
    def post_list(start_after: int = None, end_before: int = None) -> Response:
        posts, count = search_posts.execute(start_after=start_after, end_before=end_before)

        return jsonable_encoder({
            'results': [post.to_dict() for post in posts],
            'count': count
        })

    @post_router.get('/{post_id}')
    def post_detail(post_id: int) -> Response:
        post = get_post.execute(post_id=post_id)
        return jsonable_encoder(post.to_dict())

    return post_router


def create_post_error_handlers() -> ErrorHandlers:
    error_handlers = ErrorHandlers()

    @error_handlers.handle(PostNotFound)
    def post_not_found(request: Request, exc: PostNotFound):
        status = 404
        title = 'Post Not Found'
        loc = ['path', 'post_id']
        # response = ErrorResponse(status, title, str(exc), request.url.path)
        response = create_error_response(status, title, loc, str(exc), request.url.path)
        return JSONResponse(
            status_code=status,
            content=jsonable_encoder(response.to_dict())
        )

    return error_handlers
