# ShielDoc

A Python internship portfolio project that detects potentially sensitive
information in PDF and DOCX documents and replaces detected text in
DOCX body paragraphs.

## Setup

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Usage

Run commands from the repository root.

Detect PII:

```powershell
python -m app.main "samples/synthetic.pdf"
python -m app.main "samples/synthetic.docx"
```

Create a separate redacted DOCX:

```powershell
python -m app.main "samples/synthetic.docx" --output "samples/redacted_copy.docx"
```

The output file must not already exist.

## Supported detection

- Common ASCII email addresses.
- International phone formats for Russia and five Central Asian countries.
- Russian INN candidates with matching checksums.
- Russian internal passport details following a passport label.
- Capitalized three-part Cyrillic names following `ФИО:`.
- Single-line address fields beginning with `Адрес:`.

## Architecture

Extractors return text records with page or paragraph numbers.
The analyzer coordinates detectors, which return `PIIEntity` objects.
The DOCX redactor groups entities by paragraph and replaces their spans.

Offsets are relative to each record's original text:
`text[entity.start:entity.end] == entity.value`.

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests use synthetic data.

## Limitations

- PDF extraction requires an existing text layer; OCR is not implemented.
- PDF redaction is not implemented.
- DOCX detection covers body paragraphs, not tables, headers, or footers.
- Replacing a DOCX paragraph removes its inline formatting and embedded content.
- Comments, metadata, and other stored document content are not sanitized.
- Detection can miss PII or produce false positives.
- A matching INN checksum does not prove the identifier was issued.
- Confidence values are fixed defaults, not measured probabilities.

This is a limited MVP, not a guarantee of complete anonymization.