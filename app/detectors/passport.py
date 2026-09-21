import re

from app.models.pii import PIIEntity


PASSPORT_PATTERN = re.compile(
    r"\bпаспорт\b"
    r"[ \t\u00a0]*:?[ \t\u00a0]*"
    r"(?:серия[ \t\u00a0]+)?"
    r"(?:№[ \t\u00a0]*)?"
    r"(?P<passport>"
    r"[0-9]{2}[ \t\u00a0]?[0-9]{2}"
    r"[ \t\u00a0]+"
    r"(?:(?:номер|№)[ \t\u00a0]*)?"
    r"[0-9]{6}"
    r")"
    r"(?!\w)",
    re.IGNORECASE,
)


def detect_passports(
    text: str,
    page: int | None = None,
) -> list[PIIEntity]:
    entities = []

    for match in PASSPORT_PATTERN.finditer(text):
        entities.append(
            PIIEntity(
                type="PASSPORT",
                value=match.group("passport"),
                page=page,
                start=match.start("passport"),
                end=match.end("passport"),
                confidence=1.0,
            )
        )

    return entities