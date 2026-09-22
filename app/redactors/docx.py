from pathlib import Path

from docx import Document

from app.models.pii import PIIEntity
from app.redactors.text import redact_text


def redact_docx(
    input_path: str | Path,
    output_path: str | Path,
    entities: list[PIIEntity],
) -> None:
    source = Path(input_path)
    destination = Path(output_path)

    if source.resolve() == destination.resolve():
        raise ValueError("Output must be different from the original file.")

    document = Document(str(source))
    paragraphs = document.paragraphs

    by_paragraph: dict[int, list[PIIEntity]] = {}

    for entity in entities:
        number = entity.paragraph

        if entity.page is not None or number is None:
            raise ValueError("Each entity must have a DOCX paragraph location.")

        if not 1 <= number <= len(paragraphs):
            raise ValueError("Entity paragraph number is outside the document.")

        by_paragraph.setdefault(number, []).append(entity)

    removed_link_ids: set[str] = set()

    for number, paragraph_entities in by_paragraph.items():
        paragraph = paragraphs[number - 1]

        # Remember links belonging to the content we will replace.
        removed_link_ids.update(
            paragraph._p.xpath(".//w:hyperlink/@r:id")
        )

        paragraph.text = redact_text(paragraph.text, paragraph_entities)

    # A relationship may also be used by an unchanged paragraph.
    referenced_ids = set(document.element.xpath(".//@r:id"))

    for relationship_id in removed_link_ids:
        if relationship_id not in referenced_ids:
            document.part.drop_rel(relationship_id)

    # Exclusive creation: fail if the destination already exists.
    with destination.open("xb") as output:
        document.save(output)   