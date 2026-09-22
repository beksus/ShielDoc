from app.models.pii import PIIEntity


def redact_text(text: str, entities: list[PIIEntity]) -> str:
    """Replace detected spans in one text record with [REDACTED]."""
    spans = []

    for entity in entities:
        if not 0 <= entity.start < entity.end <= len(text):
            raise ValueError("Entity offsets are outside the text.")

        if text[entity.start:entity.end] != entity.value:
            raise ValueError("Entity value does not match its text span.")

        spans.append((entity.start, entity.end))

    spans.sort()

    merged: list[tuple[int, int]] = []

    for start, end in spans:
        if merged and start < merged[-1][1]:
            previous_start, previous_end = merged[-1]
            merged[-1] = (previous_start, max(previous_end, end))
        else:
            merged.append((start, end))

    parts = []
    cursor = 0

    for start, end in merged:
        parts.append(text[cursor:start])
        parts.append("[REDACTED]")
        cursor = end

    parts.append(text[cursor:])

    return "".join(parts)