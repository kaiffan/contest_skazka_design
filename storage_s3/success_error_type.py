from typing import NamedTuple, Union


class Error(NamedTuple):
    message: str


class Success(NamedTuple):
    value: str


FileUploadResult = Union[Success, Error]
