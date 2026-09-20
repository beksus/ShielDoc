from docx import Document

def extract_docx(path):
    doc = Document(path)

    paragraphs = []

    for index, paragraph in enumerate(doc.paragraphs):
        paragraphs.append({
            "paragraph": index + 1,
            "text": paragraph.text
        })

    return paragraphs