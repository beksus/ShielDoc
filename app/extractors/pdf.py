import pymupdf


def extract_pdf(path: str) -> list[dict]:
    pages = []

    with pymupdf.open(path) as doc:
        if doc.needs_pass:
            raise ValueError("Password-protected PDFs are not supported.")
        for page_number, page in enumerate(doc, start=1):
            pages.append({
                "page": page_number,
                "text": page.get_text(),
            })

    return pages