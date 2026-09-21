import re

from app.models.pii import PIIEntity


INN_PATTERN = re.compile(r"(?<![\w+])[0-9]{10}(?:[0-9]{2})?(?!\w)")


def _calculate_check_digit(number: str, weights: tuple[int, ...]) -> int:
    total = sum(
        int(digit) * weight
        for digit, weight in zip(number, weights)
    )
    return total % 11 % 10


def has_valid_inn_checksum(number: str) -> bool:
    if len(number) not in (10, 12):
        return False

    if not number.isascii() or not number.isdigit():
        return False

    # All-zero placeholders pass the arithmetic but aren't useful candidates.
    if number == "0" * len(number):
        return False

    if len(number) == 10:
        check_digit = _calculate_check_digit(
            number[:9],
            (2, 4, 10, 3, 5, 9, 4, 6, 8),
        )
        return check_digit == int(number[9])

    first_check_digit = _calculate_check_digit(
        number[:10],
        (7, 2, 4, 10, 3, 5, 9, 4, 6, 8),
    )
    second_check_digit = _calculate_check_digit(
        number[:11],
        (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8),
    )

    return (
        first_check_digit == int(number[10])
        and second_check_digit == int(number[11])
    )

def detect_inns(text: str, page: int | None = None) -> list[PIIEntity]:
    entities = []

    for match in INN_PATTERN.finditer(text):
        number = match.group()

        if not has_valid_inn_checksum(number):
            continue

        entities.append(
            PIIEntity(
                type="INN",
                value=number,
                page=page,
                start=match.start(),
                end=match.end(),
                confidence=1.0,
            )
        )

    return entities