import fitz

def extract_pdf(path):
    doc = fitz.open(path)

    pages = []

    for page_number, page in enumerate(doc):
        text = page.get_text()

        pages.append({
            "page": page_number + 1,
            "text": text
        })

    return pages