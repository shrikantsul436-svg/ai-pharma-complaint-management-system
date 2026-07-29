"""
Turns an uploaded complaint document (PDF, DOCX, TXT, EML) into plain text
that we can hand to the LLM. This is intentionally simple - the assignment
explicitly says production-grade OCR/parsing is not required.
"""
import email
import io
from email import policy

from pypdf import PdfReader
from docx import Document


def parse_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


def parse_eml(file_bytes: bytes) -> str:
    msg = email.message_from_bytes(file_bytes, policy=policy.default)
    subject = msg.get("subject", "")
    sender = msg.get("from", "")
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body += part.get_content()
    else:
        body = msg.get_content()
    return f"From: {sender}\nSubject: {subject}\n\n{body}"


def parse_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text(filename: str, file_bytes: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return parse_pdf(file_bytes)
    if lower.endswith(".docx"):
        return parse_docx(file_bytes)
    if lower.endswith(".eml"):
        return parse_eml(file_bytes)
    if lower.endswith(".txt"):
        return parse_txt(file_bytes)
    # Fallback: best-effort decode
    return parse_txt(file_bytes)
