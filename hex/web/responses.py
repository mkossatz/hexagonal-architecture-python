from dataclasses import dataclass
from datetime import datetime
from dataclasses_json import dataclass_json, LetterCase


class Timestamp(str):

    @classmethod
    def from_datetime(cls, dt: datetime):
        return cls(dt.strftime("%m/%d/%Y, %H:%M:%S"))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Detail:
    loc: list
    msg: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ErrorResponse:
    status: int
    title: str
    detail: Detail
    path: str
    timestamp: Timestamp


def create_error_response(
    status: int,
    title: str,
    loc: list,
    msg: str,
    path: str
) -> ErrorResponse:
    return ErrorResponse(
        status, title,
        Detail(loc, msg),
        path,
        Timestamp.from_datetime(datetime.now())
    )
