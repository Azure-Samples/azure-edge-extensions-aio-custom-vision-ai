from typing import TypeVar
from io.writer import Writer
from io.loader import Loader

T = TypeVar("T", bound=Writer)
U = TypeVar("U", bound=Loader)
