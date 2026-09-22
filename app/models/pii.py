from dataclasses import dataclass


@dataclass
class PIIEntity:
    type: str
    value: str
    page: int | None
    start: int
    end: int
    confidence: float = 1.0
    paragraph: int | None = None