import re
from typing import Dict, Any
from .utils import normalize_date, find_last4

def detect_bank_and_parse(text: str) -> Dict[str, Any]:
    return {"bank": "KOTAK", "fields": parse_kotak(text)}

def parse_kotak(text: str) -> Dict[str, Any]:
    fields = {
        "last4": "",
        "statement_date": "",
        "billing_cycle_start": "",
        "billing_cycle_end": "",
        "payment_due_date": "",
        "total_balance": "",
        "minimum_due": "",
        "transactions": [],
    }

    # ---- Last 4 digits ----
    fields["last4"] = find_last4(text) or ""


    # ---- Statement Date ----
    m = re.search(r"Statement\s+Date\s+([0-9]{1,2}[-/A-Za-z]+[-/0-9]+)", text)
    if m:
        fields["statement_date"] = normalize_date(m.group(1))

    # ---- Billing Cycle ----
    m = re.search(r"Transaction\s+details\s+from\s+([A-Za-z0-9-]+)\s+to\s+([A-Za-z0-9-]+)", text)
    if m:
        fields["billing_cycle_start"] = normalize_date(m.group(1))
        fields["billing_cycle_end"] = normalize_date(m.group(2))

    # ---- Payment Due Date ----
    m_due = re.search(
     r"Remember\s*to\s*pay\s*by\s*([0-9]{1,2}[-/][A-Za-z]{3}[-/][0-9]{4})",
     text,
     re.IGNORECASE
   )
    if m_due:
     fields["payment_due_date"] = normalize_date(m_due.group(1))


    # ---- Total Amount Due ----
    m = re.search(r"Total\s+Amount\s+Due.*?Rs\.?\s?([0-9,]+\.\d{2})", text)
    if m:
        fields["total_balance"] = m.group(1).replace(",", "")

    # ---- Minimum Amount Due ----
    m = re.search(r"Minimum\s+Amount\s+Due.*?Rs\.?\s?([0-9,]+\.\d{2})", text)
    if m:
        fields["minimum_due"] = m.group(1).replace(",", "")

    # ---- Transactions ----
    fields["transactions"] = extract_transactions(text)

    return fields


def extract_transactions(text: str):
    """
    Extract transaction rows (date + description + amount)
    """
    txs = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        m = re.match(r"(\d{1,2}/\d{1,2}/\d{4})\s+(.*?)\s+([0-9,]+\.\d{2})(?:\s*Cr)?$", line)
        if m:
            txs.append({
                "date": normalize_date(m.group(1)),
                "description": re.sub(r"\s+", " ", m.group(2)),
                "amount": m.group(3).replace(",", "")
            })
    return txs
