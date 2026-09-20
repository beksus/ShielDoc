from app.detectors.email import detect_emails

text = """
Договор заключен с Ивановым Иваном.

Email: ivan.petrov@gmail.com
Дополнительная почта: work@example.org
"""

results = detect_emails(text, page=1)

for result in results:
    print(result)