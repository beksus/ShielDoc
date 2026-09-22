# ShielDoc

A Python internship portfolio project that detects potentially sensitive
information in PDF and DOCX documents and creates separate redacted copies.
PDF redaction removes detected text from matched page regions and fills those
regions with black rectangles. DOCX redaction replaces detected body-paragraph
text with `[REDACTED]`.

## Setup

Requires Python 3.10 or newer. The current setup was verified on Windows with
Python 3.14, PyMuPDF 1.28.2, and python-docx 1.2.0.

Run these PowerShell commands from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If activation is unavailable, use `.\.venv\Scripts\python.exe` instead of
`python` in the installation and application commands.

## Usage

Run commands from the repository root. Included samples contain synthetic data.

Detect PII without modifying the document:

```powershell
python -m app.main "samples/synthetic.pdf"
python -m app.main "samples/synthetic.docx"
```

Create separate redacted copies:

```powershell
python -m app.main "samples/synthetic.pdf" --output "samples/redacted_copy.pdf"
python -m app.main "samples/synthetic.docx" --output "samples/redacted_copy.docx"
```

The output must have the same extension as the input, its parent folder must
exist, and the output file must not already exist. The original is not modified.
Choose a new output filename when repeating a command.

The CLI prints detected types, original values, page or paragraph numbers, and
character offsets. When saving a copy, the printed matches still describe the
original input. These values can be sensitive if you use your own documents.

Inspect the saved copy and rerun detection on it:

```powershell
python -m app.main "samples/redacted_copy.pdf"
python -m app.main "samples/redacted_copy.docx"
```

`No PII detected.` means the implemented detectors found no matches in the
extracted content. It does not guarantee that the whole file is anonymized.

## Supported detection

| Type | Current scope |
| --- | --- |
| Email | Common ASCII email addresses. |
| Phone | International numbers beginning with `+7` (Russia/Kazakhstan), `+992` (Tajikistan), `+993` (Turkmenistan), `+996` (Kyrgyzstan), or `+998` (Uzbekistan), with country-specific digit counts. Spaces, nonbreaking spaces, and hyphens are supported; parentheses around a three-digit code are supported for `+7`. |
| INN | Russian 10- and 12-digit candidates with matching checksums. |
| Passport | Russian internal passport series and number following `Паспорт`, including supported `серия` and `номер`/`№` forms. |
| Person | Capitalized three-part Cyrillic names following `ФИО:`, including supported hyphenated parts. |
| Address | A nonempty single-line field beginning with `Адрес:`; the exact `[REDACTED]` marker is ignored. |

## Architecture

```text
PDF / DOCX
    -> extractor
    -> text records with page or paragraph numbers
    -> analyzer
    -> individual detectors
    -> list[PIIEntity]
    -> CLI output and optional format-specific redactor
```

Extractors read document text. The analyzer coordinates detectors and attaches
DOCX paragraph numbers; detection rules stay in the individual detector modules.
All detectors return the shared `PIIEntity` dataclass.

Page and paragraph numbers are one-based. Character offsets are relative to
each record's original text, with an inclusive start and exclusive end:
`text[entity.start:entity.end] == entity.value`.

Results follow record order and then detector-call order, rather than being
globally sorted by their position in the text.

The DOCX redactor groups entities by paragraph. Its text helper validates spans,
merges overlaps, and builds replacement text from the original string so that
earlier replacements do not shift later offsets.

The PDF redactor validates entities against page text and searches for matching
rectangles. Each value must resolve to one rectangle with matching text on its
page. All locations are checked before redactions are applied. The result is
serialized to bytes and written to a new file.

## Tests

```powershell
python -m unittest discover -s tests -v
```

The current suite contains 60 tests and passed in a fresh virtual environment.
Tests cover detector behavior, analyzer integration, extraction pipelines, text
replacement, and saving redacted copies. Fixtures use synthetic data; document
integration tests create temporary files.

## Limitations

- PDF extraction requires an existing text layer; OCR is not implemented.
- PDF redaction currently rejects values that resolve to multiple rectangles,
  including repeated values on the same page and multiline matches. Unmatched
  values or rectangle-text mismatches also cause an error.
- PDF redaction targets text only. Images and vector drawings are preserved;
  text overlapping a redaction rectangle can also be removed. Inspect the output
  visually for unintended changes.
- DOCX detection covers body paragraphs, not tables, headers, or footers.
- Replacing a DOCX paragraph preserves paragraph-level formatting but removes
  inline formatting and embedded content within that changed paragraph.
- Comments, metadata, attachments, and other stored document content are not
  comprehensively sanitized.
- Phone detection checks supported formats and lengths, not whether a number
  is assigned. Domestic formats without an international `+` prefix are excluded.
- A matching INN checksum does not prove the identifier was issued. Other CIS
  countries' tax identifiers are not implemented.
- Name detection requires a supported label and capitalization; it does not
  find names throughout ordinary prose. Address detection accepts arbitrary
  labeled values and captures additional fields if they share the address line.
- Detection can miss PII or produce false positives. Different detectors may
  return overlapping spans.
- Confidence values are fixed defaults, not measured probabilities.

This is a limited MVP, not a guarantee of complete anonymization.
