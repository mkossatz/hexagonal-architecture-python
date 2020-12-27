import inject
from fastapi import FastAPI

from hex.configuration import inject_dependencies
from hex.web.routes.post import create_post_router, create_post_error_handlers
from hex.web.error_handlers import inject_error_handlers, create_default_error_handlers


@inject_dependencies
def create_application() -> FastAPI:

    app = FastAPI(
        title="Hexagonal Architecture Example Project",
        description="This project is designed to be used as a template for the development of services.",
        version="0.1"
    )

    app.include_router(create_post_router())
    app = inject_error_handlers(app, create_post_error_handlers())

    app = inject_error_handlers(app, create_default_error_handlers())

    return app
