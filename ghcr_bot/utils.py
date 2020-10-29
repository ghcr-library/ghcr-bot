from dataclasses import dataclass
from typing import List


@dataclass
class ImageInfo:
    name: str
    tags: List[str]

