from app.detectors.email import detect_emails
from app.detectors.phone import detect_phones
from app.models.pii import PIIEntity
from app.detectors.inn import detect_inns
from app.detectors.passport import detect_passports


def analyze_pages(pages: list[dict]) -> list[PIIEntity]:
    results = []

    for record in pages:
        text = record["text"]
        page_number = record.get("page")

        results.extend(detect_emails(text, page=page_number))
        results.extend(detect_phones(text, page=page_number))
        results.extend(detect_inns(text, page=page_number))
        results.extend(detect_passports(text, page=page_number))

    return results