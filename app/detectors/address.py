import re

from app.models.pii import PIIEntity


ADDRESS_PATTERN = re.compile(
    r"^[ \t\u00a0]*адрес[ \t\u00a0]*:[ \t\u00a0]*"
    r"(?P<address>[^\r\n]+)",
    re.IGNORECASE | re.MULTILINE,
)


def detect_addresses(
    text: str,
    page: int | None = None,
) -> list[PIIEntity]:
    entities = []

    for match in ADDRESS_PATTERN.finditer(text):
        raw_value = match.group("address")
        value = raw_value.strip()

        if not value:
            continue

        leading_spaces = len(raw_value) - len(raw_value.lstrip())
        start = match.start("address") + leading_spaces

        entities.append(
            PIIEntity(
                type="ADDRESS",
                value=value,
                page=page,
                start=start,
                end=start + len(value),
                confidence=1.0,
            )
        )

    return entities