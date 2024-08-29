from dataclasses import dataclass
from typing import Tuple


@dataclass
class NamedEntity:
    span: Tuple[int, int]
    label: str
    text: str
