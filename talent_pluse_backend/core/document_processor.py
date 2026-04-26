import os
import io
import re
import pandas as pd
import pdfplumber
import trafilatura

from bs4 import BeautifulSoup
from docx import Document


# --------------------------------------------
# Config
# --------------------------------------------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))


# --------------------------------------------
# Helpers
# --------------------------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def chunk_text(text: str):
    text = clean_text(text)

    if not text:
        return []

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + CHUNK_SIZE, length)

        if end < length:
            split = max(
                text.rfind(". ", start, end),
                text.rfind("\n", start, end)
            )

            if split > start + 300:
                end = split + 1

        piece = text[start:end].strip()

        if piece:
            chunks.append(piece)

        if end >= length:
            break

        start = end - CHUNK_OVERLAP

    return chunks


# --------------------------------------------
# File Processing
# --------------------------------------------
def process_file_bytes(raw: bytes, filename: str):
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        return process_txt(raw)

    if ext == ".pdf":
        return process_pdf(raw)

    if ext == ".docx":
        return process_docx(raw)

    if ext == ".csv":
        return process_csv(raw)

    return []


def process_txt(raw: bytes):
    text = raw.decode("utf-8", errors="ignore")
    return chunk_text(text)


def process_pdf(raw: bytes):
    pages = []

    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            if txt.strip():
                pages.append(txt)

    return chunk_text("\n\n".join(pages))


def process_docx(raw: bytes):
    doc = Document(io.BytesIO(raw))

    lines = []
    for p in doc.paragraphs:
        if p.text.strip():
            lines.append(p.text)

    return chunk_text("\n".join(lines))


def process_csv(raw: bytes):
    df = pd.read_csv(io.BytesIO(raw)).fillna("")

    rows = []

    for _, row in df.iterrows():
        vals = [f"{col}: {row[col]}" for col in df.columns]
        rows.append(" | ".join(vals))

    return chunk_text("\n".join(rows))


# --------------------------------------------
# Web URL Processing
# --------------------------------------------
def process_web_url(url: str):
    try:
        downloaded = trafilatura.fetch_url(url)

        if downloaded:
            text = trafilatura.extract(downloaded)

            if text:
                return chunk_text(text)

    except Exception:
        pass

    # fallback parser
    try:
        import requests

        res = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        soup = BeautifulSoup(res.text, "lxml")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        return chunk_text(text)

    except Exception:
        return []