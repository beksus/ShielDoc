import fitz


def extract_pdf(path: str) -> list[dict]:
    pages = []

    with fitz.open(path) as doc:
        for page_number, page in enumerate(doc, start=1):
            pages.append({
                "page": page_number,
                "text": page.get_text(),
            })

    return pages