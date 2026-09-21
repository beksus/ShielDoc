import re

from app.models.pii import PIIEntity


NAME_PART = r"[А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?"

PERSON_PATTERN = re.compile(
    r"(?i:\bфио\b)"
    r"[ \t\u00a0]*:[ \t\u00a0]*"
    r"(?P<person>"
    + NAME_PART
    + r"[ \t\u00a0]+"
    + NAME_PART
    + r"[ \t\u00a0]+"
    + NAME_PART
    + r")"
    r"(?![\w-])"
)


def detect_persons(
    text: str,
    page: int | None = None,
) -> list[PIIEntity]:
    entities = []

    for match in PERSON_PATTERN.finditer(text):
        entities.append(
            PIIEntity(
                type="PERSON",
                value=match.group("person"),
                page=page,
                start=match.start("person"),
                end=match.end("person"),
                confidence=1.0,
            )
        )

    return entities