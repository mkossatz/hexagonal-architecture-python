from typing import Type
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from hex.web.responses import create_error_response

from json import dumps


class ErrorHandlers:
    def __init__(self):
        self.handlers = {}

    def handle(self, ExceptionClass):
        def wrap(handler):
            self.handlers[ExceptionClass] = handler
            return handler
        return wrap


def inject_error_handlers(app: FastAPI, error_handlers: ErrorHandlers) -> FastAPI:
    for ExceptionClass, handler in error_handlers.handlers.items():
        app.add_exception_handler(ExceptionClass, handler)
    return app


def create_default_error_handlers() -> ErrorHandlers:
    error_handlers = ErrorHandlers()

    @error_handlers.handle(RequestValidationError)
    def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        status = 400
        title = 'Bad Request'
        msg = 'Cannot or will not process the request due to request being malformed.'
        loc = exc.errors()[0]['loc']
        msg = exc.errors()[0]['msg']
        response = create_error_response(status, title, loc, msg, request.url.path)
        return JSONResponse(
            status_code=status,
            content=response.to_dict()
        )

    @error_handlers.handle(Exception)
    def handle_unknown_error(request: Request, exc: Exception) -> JSONResponse:
        status = 500
        title = 'Internal Server Error'
        msg = 'Something went wrong on our side.'
        response = create_error_response(status, title, [], msg, request.url.path)
        return JSONResponse(
            status_code=status,
            content=jsonable_encoder(response.to_dict())
        )

    return error_handlers
