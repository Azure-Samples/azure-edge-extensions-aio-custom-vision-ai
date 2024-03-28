from typing import TypeVar
from media_io.writer import Writer
from media_io.loader import Loader

T = TypeVar("T", bound=Writer)
U = TypeVar("U", bound=Loader)
