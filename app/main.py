import argparse
from pathlib import Path

from app.analyzer import analyze_pages
from app.extractors.docx import extract_docx
from app.extractors.pdf import extract_pdf
from app.redactors.docx import redact_docx


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect PII in a PDF or DOCX document."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to a PDF or DOCX file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save a redacted DOCX copy to a new file",
    )
    args = parser.parse_args()

    path = args.path

    if not path.is_file():
        parser.error(f"File not found: {path}")

    extension = path.suffix.lower()

    if args.output is not None:
        if extension != ".docx":
            parser.error("--output currently supports DOCX input only.")

        if args.output.suffix.lower() != ".docx":
            parser.error("The output filename must end with .docx.")

    if extension == ".pdf":
        records = extract_pdf(str(path))
    elif extension == ".docx":
        records = extract_docx(str(path))
    else:
        parser.error("Supported file types: .pdf and .docx")

    entities = analyze_pages(records)

    if args.output is not None:
        try:
            redact_docx(path, args.output, entities)
        except (OSError, ValueError) as error:
            parser.error(str(error))

        print(f"Saved DOCX copy: {args.output}")
        print(
            "Only detected body-paragraph text was replaced. "
            "Other document content was not checked."
        )

    if not entities:
        print("No PII detected.")
        return

    print(f"Detected {len(entities)} PII matches:\n")

    for entity in entities:
        if entity.page is not None:
            location = f"page {entity.page}"
        elif entity.paragraph is not None:
            location = f"paragraph {entity.paragraph}"
        else:
            location = "unknown location"

        print(
            f"{entity.type} | {location} | "
            f"characters {entity.start}:{entity.end} | "
            f"{entity.value}"
        )


if __name__ == "__main__":
    main()