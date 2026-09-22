import pymupdf
from pathlib import Path

from app.models.pii import PIIEntity


def find_entity_rectangle(
        page: pymupdf.Page,
        entity: PIIEntity,
) -> pymupdf.Rect:
    """Locate one unambiguous, single-line entity on its PDF page."""
    if entity.page != page.number + 1 or entity.paragraph is not None:
        raise ValueError("Entity does not belong to this PDF page.")

    text = page.get_text()

    if not 0 <= entity.start < entity.end <= len(text):
        raise ValueError("Entity offsets are outside the page text.")

    if text[entity.start:entity.end] != entity.value:
        raise ValueError("Entity value does not match its text span.")

    rectangles = page.search_for(entity.value)

    if len(rectangles) != 1:
        raise ValueError(
            "Expected one rectangle; repeated or multiline matches "
            "are not supported yet."
        )

    rectangle = rectangles[0]

    if page.get_textbox(rectangle) != entity.value:
        raise ValueError("Located rectangle does not match the exact value.")

    return rectangle

def redact_pdf(
    input_path: str | Path,
    output_path: str | Path,
    entities: list[PIIEntity],
) -> None:
    source = Path(input_path)
    destination = Path(output_path)

    if source.resolve() == destination.resolve():
        raise ValueError("Output must be different from the original file.")

    with pymupdf.open(str(source)) as document:
        locations: list[tuple[int, pymupdf.Rect]] = []

        # Validate every location before modifying any page.
        for entity in entities:
            if entity.page is None:
                raise ValueError("PDF entities must have a page number.")

            if not 1 <= entity.page <= len(document):
                raise ValueError("Entity page is outside the document.")

            page_index = entity.page - 1
            rectangle = find_entity_rectangle(
                document[page_index],
                entity,
            )
            locations.append((page_index, rectangle))

        changed_pages = set()

        for page_index, rectangle in locations:
            document[page_index].add_redact_annot(
                rectangle,
                fill=(0, 0, 0),
            )
            changed_pages.add(page_index)

        for page_index in changed_pages:
            document[page_index].apply_redactions(
                images=0,
                graphics=0,
                text=0,
            )

        pdf_bytes = document.tobytes(garbage=4, deflate=True)

    # The source document is now closed.
    with destination.open("xb") as output:
        output.write(pdf_bytes)