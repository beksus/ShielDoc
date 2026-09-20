from app.detectors.email import detect_emails


def analyze_pages(pages):
    results = []

    for page in pages:
        entities = detect_emails(
            text=page["text"],
            page=page["page"]
        )

        results.extend(entities)

    return results