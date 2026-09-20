import re

from app.models.pii import PIIEntity


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


def detect_emails(text: str, page: int | None = None) -> list[PIIEntity]:
    entities = []

    for match in EMAIL_PATTERN.finditer(text):
        entities.append(
            PIIEntity(
                type="EMAIL",
                value=match.group(),
                page=page,
                start=match.start(),
                end=match.end(),
                confidence=1.0,
            )
        )

    return entities