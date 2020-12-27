import os

import inject
from fastapi import FastAPI

from hex.adapters.database.postgres import PostsRepository
from hex.domain.repositories.posts_repository import PostsRepositoryInterface


def config(binder: inject.Binder) -> None:
    binder.bind(
        PostsRepositoryInterface,
        PostsRepository(os.getenv('DATABASE_URI')))


def inject_dependencies(create_application):
    def wrapper(*args, **kwargs):
        inject.configure(config)
        return create_application(*args, **kwargs)
    return wrapper
