import re


def normalize_query_text(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"https?://\S+", " url ", text)
    text = re.sub(r"www\.\S+", " url ", text)
    text = re.sub(r"(\w+)\.(pdf|csv|xlsx|docx|txt)\b", r"\1 file \2 ", text)
    text = text.replace("_", " ")
    text = re.sub(r"whats\b", "what is", text)
    text = re.sub(r"whats\b", "what is", text)
    text = re.sub(r"\bpls\b", "please", text)
    text = re.sub(r"\bplz\b", "please", text)
    text = re.sub(r"\binfo\b", "information", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
