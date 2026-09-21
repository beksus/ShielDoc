import re

from app.models.pii import PIIEntity


PHONE_PATTERN = re.compile(
    r"(?<![\w+])"
    r"\+"
    r"(?:"
    r"7(?:"
    r"[ \u00a0]?\([0-9]{3}\)(?:[ \u00a0-]?[0-9]){7}"
    r"|(?:[ \u00a0-]?[0-9]){10}"
    r")"
    r"|(?:992|996|998)(?:[ \u00a0-]?[0-9]){9}"
    r"|993(?:[ \u00a0-]?[0-9]){8}"
    r")"
    r"(?!\w|[ \u00a0-][0-9])"
)


def detect_phones(
    text: str,
    page: int | None = None,
) -> list[PIIEntity]:
    entities = []

    for match in PHONE_PATTERN.finditer(text):
        entities.append(
            PIIEntity(
                type="PHONE",
                value=match.group(),
                page=page,
                start=match.start(),
                end=match.end(),
                confidence=1.0,
            )
        )

    return entities