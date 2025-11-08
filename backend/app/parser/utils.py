import re
from dateutil import parser as dateparser
from typing import Optional, Dict

def text_stats(text: str) -> Dict[str, int]:
    return {"char_count": len(text or ""), "word_count": len((text or "").split())}

def normalize_date(text_date: str) -> Optional[str]:
    """
    Convert date text (like '21-Sep-2025' or '07/11/2025') → ISO 'YYYY-MM-DD'
    Force dayfirst=True for Indian-style dates.
    """
    if not text_date:
        return None
    try:
        dt = dateparser.parse(text_date, dayfirst=True, fuzzy=True)
        return dt.date().isoformat()
    except Exception:
        return None

def find_last4(text: str) -> Optional[str]:
    """
    Extract the correct last 4 digits from lines like:
    'PrimaryCardTransactions-416644XXXXXX8253'
    or 'Primary Card Transactions- 4166 XXXX XXXX 8253'
    Always returns the last 4 digits (e.g., 8253).
    """
    # Kotak-specific: PrimaryCardTransactions-416644XXXXXX8253
    m = re.search(r"Primary\s*Card\s*Transactions[-:\s]*([0-9Xx\s\-]{8,})", text, re.IGNORECASE)
    if m:
        digits = re.findall(r"\d", m.group(1))
        if len(digits) >= 4:
            return "".join(digits[-4:])  # ✅ Return only last 4 digits (e.g., 8253)

    # General fallback: match 'XXXX XXXX XXXX 8253'
    m = re.search(r"([Xx]{2,}[\s\-]*\d{4})", text)
    if m:
        digits = re.findall(r"\d", m.group(1))
        if digits:
            return "".join(digits[-4:])

    # Final fallback: last 4-digit number not a year
    nums = re.findall(r"\b(\d{4})\b", text)
    for token in reversed(nums):
        if not (1900 <= int(token) <= 2099):
            return token
    return None

