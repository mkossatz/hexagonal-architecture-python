from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import dataclass_json, LetterCase


class Timestamp(str):

    @classmethod
    def from_datetime(cls, dt: datetime):
        return cls(dt.strftime("%m/%d/%Y, %H:%M:%S"))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Post:
    id: int
    author_name: str
    title: str
    body: str
    created_at: Timestamp
    updated_at: Timestamp
