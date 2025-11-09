import re

def find_date_near_label(text: str, label_regex: str, window_after: int = 220, window_before: int = 40):
    date_token = r"([A-Za-z]{3,9}\s+\d{1,2},?\s*\d{4}|\d{1,2}\s+[A-Za-z]{3,9}\s+'?\d{2,4}|\d{1,2}/\d{1,2}/\d{4})"
    m = re.search(label_regex, text, re.IGNORECASE)
    if not m:
        # try global pattern: label followed by date anywhere nearby
        m2 = re.search(rf"{label_regex}[\s\S]{{0,{window_after}}}{date_token}", text, re.IGNORECASE)
        if m2:
            return m2.group(m2.lastindex).strip()
        return None
    after = text[m.end(): m.end() + window_after]
    m_after = re.search(date_token, after, re.IGNORECASE)
    if m_after:
        return m_after.group(1).strip()
    before = text[max(0, m.start() - window_before): m.start()]
    m_before = re.search(date_token, before, re.IGNORECASE)
    if m_before:
        return m_before.group(1).strip()
    m_near = re.search(rf"{label_regex}[\s\S]{{0,{window_after}}}{date_token}", text, re.IGNORECASE)
    if m_near:
        return m_near.group(m_near.lastindex).strip()
    return None
from typing import Dict, Any ,List
from .utils import normalize_date, find_last4
from datetime import datetime
from typing import Dict, Any
from .utils import normalize_date, find_last4

# ✅ Detect bank and route to correct parser
def detect_bank_and_parse(text: str) -> Dict[str, Any]:
    text_upper = text.upper()
    if "ICICI BANK" in text_upper:
        return {"bank": "ICICI", "fields": parse_icici(text)}
    elif "KOTAK" in text_upper:
        return {"bank": "KOTAK", "fields": parse_kotak(text)}
    elif "AXIS BANK" in text_upper:
        return {"bank": "AXIS", "fields": parse_axis(text)}
    elif "HDFC BANK" in text_upper:
        return {"bank": "HDFC", "fields": parse_hdfc(text)}
    elif "SBI" in text_upper:
        return {"bank": "SBI", "fields": parse_sbi(text)}
    else:
        return {"bank": "UNKNOWN", "fields": {}}


# ---------------------- kotak bank PARSER-----------------
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


# ----------------------- ICICI BANK PARSER ----------------------


import re
from typing import Dict, Any
from datetime import datetime

# small date normalizer used by ICICI parser
def normalize_date_icici(s: str) -> str:
    """Normalize a variety of human date tokens to ISO YYYY-MM-DD. Return original stripped string on failure."""
    if not s:
        return ""
    s0 = s.strip().replace("’", "'").replace("‘", "'").replace(".", "").replace(",", "")
    s0 = re.sub(r"\s+", " ", s0)
    fmts = [
        "%d %b %Y", "%d %B %Y",      # "14 Oct 2025", "14 October 2025"
        "%b %d %Y", "%B %d %Y",      # "Oct 14 2025", "October 14 2025"
        "%d/%m/%Y", "%d-%m-%Y",      # "14/10/2025"
        "%Y-%m-%d"                   # ISO
    ]
    for f in fmts:
        try:
            return datetime.strptime(s0, f).strftime("%Y-%m-%d")
        except Exception:
            continue
    # Also try if input is "Oct 2025" -> return YYYY-MM-01
    m_mon = re.match(r"^([A-Za-z]{3,9})\s+(\d{4})$", s.strip())
    if m_mon:
        try:
            return datetime.strptime(m_mon.group(0), "%b %Y").strftime("%Y-%m-01")
        except Exception:
            try:
                return datetime.strptime(m_mon.group(0), "%B %Y").strftime("%Y-%m-01")
            except Exception:
                pass
    return s.strip()

def _clean_amount_raw(s: str) -> str:
    """Return amount normalized to '₹<value with 2 decimals>' or empty string."""
    if not s:
        return ""
    t = s.replace("`", "").replace("Rs.", "").replace("INR", "").replace("₹", "").strip()
    t = t.replace(",", "")
    if re.match(r"^\d+(\.\d{1,2})?$", t):
        if "." not in t:
            t = t + ".00"
        elif len(t.split(".")[1]) == 1:
            t = t + "0"
        return "₹" + t
    # if decimals missing, try to coerce numeric part
    m = re.search(r"(\d+(?:\.\d+)?)", t)
    if m:
        v = m.group(1)
        if "." not in v:
            v = v + ".00"
        elif len(v.split(".")[1]) == 1:
            v = v + "0"
        return "₹" + v
    return ""

def parse_icici(text: str) -> Dict[str, Any]:
    """
    Robust ICICI parser: extracts last4, statement_date, billing_cycle_start, billing_cycle_end,
    payment_due_date, total_balance and minimum_due.
    """
    fields = {
        "last4": "",
        # "statement_date": "",
        "billing_cycle_start": "",
        "billing_cycle_end": "",
        "payment_due_date": "",
        "total_balance": "",
        "minimum_due": "",
        "transactions": [],
    }

    # helper text zones
    top = text[:5000]  # prefer header/summary area
    flat_top = " ".join(top.split())
    flat_all = " ".join(text.split())

    # ---- last4 (prefer masked X pattern) ----
    m = re.search(r"X{4,}\s*(\d{4})", top)
    if m:
        fields["last4"] = m.group(1)
    else:
        # fallback near header
        m2 = re.search(r"(?:Card|Credit|XXXXX|XXXX)\s*[:\-]?\s*(\d{4})", top, re.IGNORECASE)
        if m2:
            fields["last4"] = m2.group(1)
        else:
            # last 4 digits anywhere in top area
            all4 = re.findall(r"\b(\d{4})\b", top)
            if all4:
                fields["last4"] = all4[-1]

    # ---- STATEMENT PERIOD (start & end) ----
    # Try explicit "Statement period" or "Billing Period"
    period_re = re.compile(
        r"(?:Statement\s+period|Statement\s+Period|Billing\s*Period)\s*[:\-]?\s*([A-Za-z0-9,\s\/\-\']+?)\s*(?:to|[-–])\s*([A-Za-z0-9,\s\/\-\']+?)\b",
        re.IGNORECASE
    )
    m_period = period_re.search(top) or period_re.search(flat_top) or period_re.search(flat_all)
    if m_period:
        start_raw = m_period.group(1).strip()
        end_raw = m_period.group(2).strip()
        fields["billing_cycle_start"] = normalize_date_icici(start_raw)
        fields["billing_cycle_end"] = normalize_date_icici(end_raw)

    # ---- STATEMENT DATE (explicit label) ----
    # Try a few forms around top-of-doc first
    # stmt_patterns = [
    #     r"Statement\s*Date\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s*\d{4})",
    #     r"Statement\s*Date\s*[:\-]?\s*([0-9]{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
    # ]
    # for p in stmt_patterns:
    #     m = re.search(p, top, re.IGNORECASE)
    #     if not m:
    #         m = re.search(p, flat_top, re.IGNORECASE)
    #     if m:
    #         fields["statement_date"] = normalize_date_icici(m.group(1))
    #         break
        # statement_date: Selected Statement Month OR Statement Date label
    m_sel = re.search(r"STATEMENT\s+DATE\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{4})", top, re.IGNORECASE)
    if m_sel:
        fields["statement_date"] = normalize_date_axis(m_sel.group(1))
    else:
        m_sd = re.search(r"Statement\s+Date\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2}\s*'?\d{2,4})", top, re.IGNORECASE)
        if m_sd:
            fields["statement_date"] = normalize_date_axis(m_sd.group(1))

    # If still empty, fall back to billing_cycle_end if available
    # ---- Billing Cycle ----
    m_cycle = re.search(
        r"Statement\s*Period\s*[:\-]?\s*([0-9]{1,2}\s*[A-Za-z]{3,9}\s*[0-9]{4})\s*(?:to|-)\s*([0-9]{1,2}\s*[A-Za-z]{3,9}\s*[0-9]{4})",
        top,
        re.IGNORECASE,
    )
    if m_cycle:
        fields["billing_cycle_start"] = normalize_date(m_cycle.group(1))
        fields["billing_cycle_end"] = normalize_date(m_cycle.group(2))

    # ---- PAYMENT DUE DATE ----
    # Prefer summary area; try multiple labeling variants
    pd_patterns = [
        r"Payment\s+Due\s+Date\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s*\d{4})",
        r"Payment\s+Due\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s*\d{4})",
        r"Pay\s+by\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s*\d{4})",
        r"Due\s+Date\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s*\d{4})",
        r"Payment\s+Due\s+Date\s*[:\-]?\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})",
    ]
    for p in pd_patterns:
        m = re.search(p, top, re.IGNORECASE)
        if not m:
            m = re.search(p, flat_top, re.IGNORECASE)
        if not m:
            m = re.search(p, flat_all, re.IGNORECASE)
        if m:
            fields["payment_due_date"] = normalize_date_icici(m.group(1))
            break

    # ---- TOTAL AMOUNT DUE / MINIMUM AMOUNT DUE ----
    # Look in top summary (left panel usually)
    total_patterns = [
        r"(?:Total\s+Amount\s+due|Total\s+Amount\s+Due|TOTAL\s+AMOUNT\s+DUE)\s*[:\n\r-]*\s*[₹`Rs\.]*\s*([0-9,]+(?:\.\d{1,2})?)",
        r"(?:Total\s+Amount\s+due|Total\s+Amount\s+Due)[\s\S]{0,40}?([0-9,]+(?:\.\d{1,2})?)"
    ]
    min_patterns = [
        r"(?:Minimum\s+Amount\s+due|Minimum\s+Amount\s+Due|Minimum\s+Amount)\s*[:\n\r-]*\s*[₹`Rs\.]*\s*([0-9,]+(?:\.\d{1,2})?)",
        r"Minimum\s+Amount\s+due[\s\S]{0,40}?([0-9,]+(?:\.\d{1,2})?)"
    ]

    def _scan_patterns(patterns, src_primary, src_fallback):
        for p in patterns:
            m = re.search(p, src_primary, re.IGNORECASE)
            if m:
                return m.group(1)
        for p in patterns:
            m = re.search(p, src_fallback, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    tot_raw = _scan_patterns(total_patterns, top, flat_top)
    min_raw = _scan_patterns(min_patterns, top, flat_top)

    # fallback to flat_all if not found in top
    if not tot_raw:
        tot_raw = _scan_patterns(total_patterns, flat_all, flat_all)
    if not min_raw:
        min_raw = _scan_patterns(min_patterns, flat_all, flat_all)

    if tot_raw:
        fields["total_balance"] = _clean_amount_raw(tot_raw)
    if min_raw:
        fields["minimum_due"] = _clean_amount_raw(min_raw)

    # ---- Transactions (reuse your existing extractor) ----
    try:
        fields["transactions"] = extract_transactions(text)
    except Exception:
        fields["transactions"] = []

    # Final sanity: avoid returning malformed placeholders
    if fields["total_balance"] == "₹" or fields["total_balance"] is None:
        fields["total_balance"] = ""
    if fields["minimum_due"] == "₹" or fields["minimum_due"] is None:
        fields["minimum_due"] = ""

    return fields







# ---------------------- AXIS BANK PARSER ----------------------
import re
from typing import Dict, Any, List, Optional
from .utils import find_last4


def normalize_date_axis(s: str) -> str:
    """
    Convert common Axis date tokens to ISO YYYY-MM-DD (or YYYY-MM-01 for month-only).
    Examples:
      "09 Oct '25" -> "2025-10-09"
      "30 Oct '25" -> "2025-10-30"
      "Oct 2025"   -> "2025-10-01"
      "09/10/2025" -> "2025-10-09"
    If parsing fails returns the original stripped string.
    """
    if not s or not s.strip():
        return ""
    s0 = s.strip()
    s0 = s0.replace("’", "'").replace("‘", "'").replace(".", "").strip()

    # Pattern: dd Mon 'yy or dd Mon yyyy   e.g. 09 Oct '25  or 09 Oct 2025
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]{3,9})\s+'?(\d{2,4})$", s0)
    if m:
        day = int(m.group(1))
        mon = m.group(2)
        yr = m.group(3)
        year = int(yr) if len(yr) == 4 else (2000 + int(yr))
        try:
            month = _month_to_num(mon)
            if 1 <= month <= 12:
                return f"{year:04d}-{month:02d}-{day:02d}"
        except Exception:
            pass

    # Pattern: Mon YYYY  e.g. Oct 2025  -> return YYYY-MM-01
    m = re.match(r"^([A-Za-z]{3,9})\s+(\d{4})$", s0)
    if m:
        month = _month_to_num(m.group(1))
        year = int(m.group(2))
        return f"{year:04d}-{month:02d}-01"

    # Pattern: dd/mm/yyyy or dd-mm-yyyy or dd.mm.yyyy
    m = re.match(r"^(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})$", s0)
    if m:
        d = int(m.group(1)); mo = int(m.group(2)); y = int(m.group(3))
        if y < 100:
            y = 2000 + y
        return f"{y:04d}-{mo:02d}-{d:02d}"

    # Pattern: yyyy-mm-dd
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s0)
    if m:
        return s0

    # fallback: return stripped input (caller can detect non-ISO)
    return s0

def _month_to_num(name: str) -> int:
    name = name.strip().lower()
    months = {
        "jan": 1, "january": 1,
        "feb": 2, "february": 2,
        "mar": 3, "march": 3,
        "apr": 4, "april": 4,
        "may": 5,
        "jun": 6, "june": 6,
        "jul": 7, "july": 7,
        "aug": 8, "august": 8,
        "sep": 9, "sept": 9, "september": 9,
        "oct": 10, "october": 10,
        "nov": 11, "november": 11,
        "dec": 12, "december": 12,
    }
    return months.get(name[:3].lower(), months.get(name, 0))


def _axis_clean_amount(s: str) -> str:
    if not s:
        return ""
    s = s.replace(",", "").replace("`", "").strip()
    s = re.sub(r"^(Rs\.?|INR|₹)\s*", "", s, flags=re.IGNORECASE)
    # ensure two decimals
    if re.match(r"^\d+(\.\d{1,2})?$", s):
        if "." not in s:
            s = s + ".00"
        elif len(s.split(".")[1]) == 1:
            s = s + "0"
    return "₹" + s


def extract_transactions_axis(text: str) -> List[Dict[str, Any]]:
    """
    Extract Axis transaction rows. This function expects the PDF-extracted plain text.
    It searches for dates that start at the beginning of a line and collects all text until
    the next date-start line as that transaction's block (so multi-line descriptions are preserved).
    """
    txs: List[Dict[str, Any]] = []

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Try to find the block start for transactions
    lower = text.lower()
    start_idx = None
    for header in ["transaction summary", "transaction details", "transaction history", "transactions for the period", "card transactions"]:
        idx = lower.find(header)
        if idx != -1:
            start_idx = idx
            break
    block = text[start_idx:] if start_idx is not None else text

    # We'll find lines that begin with a date. Use multiline flag so ^ matches line-starts.
    # Date variants handled: "09 Oct '25", "09 Oct 2025", "09/10/2025", "2025-10-09"
    date_line_re = re.compile(r"^(?P<date>\d{1,2}\s+[A-Za-z]{3,9}\s+'?\d{2,4}|\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}|\d{4}-\d{2}-\d{2})\b", re.IGNORECASE | re.MULTILINE)

    # find all date-line matches (with their positions)
    matches = list(date_line_re.finditer(block))
    if not matches:
        # Nothing matched as line-start dates -> fallback: try to parse every line that contains ₹
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            amt_m = re.search(r"(?:₹|Rs\.?)\s*([0-9,]+(?:\.[0-9]{1,2})?)", line, re.IGNORECASE)
            if amt_m:
                # try to pull a date (anywhere on the same line)
                date_any = re.search(r"(\d{1,2}\s+[A-Za-z]{3,9}\s+'?\d{2,4}|\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}|\d{4}-\d{2}-\d{2})", line)
                date_iso = normalize_date_axis(date_any.group(0)) if date_any else ""
                desc = re.sub(r"(?:₹|Rs\.?)\s*[0-9,]+(?:\.\d{1,2})?", "", line).strip()
                amt = _axis_clean_amount(amt_m.group(1))
                tx_type = "Credit" if re.search(r"\b(cr|credit|credited|cashback)\b", line, re.IGNORECASE) else ("Debit" if re.search(r"\b(dr|debit|debited|purchase|spent)\b", line, re.IGNORECASE) else "")
                txs.append({"date": date_iso, "description": re.sub(r"\s+", " ", desc), "amount": amt, "type": tx_type})
        return txs

    # For each date-line match, slice from its end to the start of next match (or end of block)
    for i, m in enumerate(matches):
        date_token = m.group("date").strip()
        start_pos = m.end()
        end_pos = matches[i+1].start() if i+1 < len(matches) else len(block)
        segment = block[start_pos:end_pos].strip()  # this includes description, maybe amount and debit/credit words

        # Normalize segment whitespace but preserve internal spaces
        seg = re.sub(r"[ \t]+", " ", segment).strip()

        # Amount extraction (prefer ₹ presence)
        amt_m = re.search(r"(?:₹|Rs\.?)\s*([0-9,]+(?:\.\d{1,2})?)", seg, re.IGNORECASE)
        if not amt_m:
            # fallback: numbers followed by optional Cr/Dr
            amt_m = re.search(r"([0-9,]+(?:\.\d{1,2})?)\s*(?:Cr|Dr|CR|DR|\bCredit\b|\bDebit\b)", seg)
        if not amt_m:
            # if still no amount, skip this row
            continue
        amt_raw = amt_m.group(1)
        amount = _axis_clean_amount(amt_raw)

        # Type: check near amount or in segment text
        type_m = re.search(r"\b(Cr|Dr|Credit|Debit|credited|debited)\b", seg, re.IGNORECASE)
        tx_type = ""
        if type_m:
            token = type_m.group(1).lower()
            if token in ("cr", "credit", "credited"):
                tx_type = "Credit"
            elif token in ("dr", "debit", "debited"):
                tx_type = "Debit"
        else:
            # heuristic
            if re.search(r"\b(refund|cashback|credited)\b", seg, re.IGNORECASE):
                tx_type = "Credit"
            elif re.search(r"\b(purchase|spent|debited|paid|withdrawal)\b", seg, re.IGNORECASE):
                tx_type = "Debit"

        # Description: everything up to the amount match
        desc = seg[:amt_m.start()].strip()
        desc = re.sub(r"\s+", " ", desc)

        # Normalize the date token to ISO using local normalizer
        date_iso = normalize_date_axis(date_token)

        txs.append({
            "date": date_iso or "",
            "description": desc,
            "amount": amount,
            "type": tx_type
        })

    return txs


def parse_axis(text: str) -> Dict[str, Any]:
    fields: Dict[str, Any] = {
        "last4": "",
        "statement_date": "",
        "billing_cycle_start": "",
        "billing_cycle_end": "",
        "payment_due_date": "",
        "total_balance": "",
        "minimum_due": "",
        "transactions": [],
    }

    # last4
    fields["last4"] = find_last4(text) or ""

    # Use top-of-document slice for summary items
    top = text[:5000].replace("\r\n", "\n").replace("\r", "\n")

    # total and minimum
    m_tot = re.search(r"(?:Total\s+Payment\s+Due|Total\s+Amount\s+Due|Total\s+Due)\s*[:\-]?\s*(?:₹|Rs\.?)?\s*([0-9,]+(?:\.\d{1,2})?)", top, re.IGNORECASE)
    if m_tot:
        fields["total_balance"] = _axis_clean_amount(m_tot.group(1))

    m_min = re.search(r"(?:Minimum\s+Payment\s+Due|Minimum\s+Amount\s+Due|Minimum\s+Due)\s*[:\-]?\s*(?:₹|Rs\.?)?\s*([0-9,]+(?:\.\d{1,2})?)", top, re.IGNORECASE)
    if m_min:
        fields["minimum_due"] = _axis_clean_amount(m_min.group(1))

        # ---------- PAYMENT DUE DATE (improved) ----------
    fields["payment_due_date"] = ""

    # date pattern that matches many formats we'll normalize later
    date_token_re = r"(\d{1,2}\s+[A-Za-z]{3,9}\s+'?\d{2,4}|\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}|\d{4}-\d{2}-\d{2}|[A-Za-z]{3,9}\s+\d{1,2},?\s*'?\d{2,4}|\b[A-Za-z]{3,9}\s+\d{4}\b)"

    # Candidate labels in order of preference (more specific first)
    pd_labels = [
        r"Payment\s+Due\s+Date",
        r"Payment\s+Due\s+On",
        r"Payment\s+Due",
        r"Pay\s+by",
        r"Due\s+Date",
        r"Last\s+Date\s+for\s+Payment",
        r"Payment\s+Due\s+Amount",  # sometimes appears but we will extract date near it
    ]

    found = False
    # Search in the top-of-document first (prefer top 5k chars)
    search_area = top  # already defined earlier as top slice

    for label in pd_labels:
        # 1) Label + date on same line
        pat_same = re.compile(rf"{label}\s*[:\-]?\s*{date_token_re}", re.IGNORECASE)
        m_same = pat_same.search(search_area)
        if m_same:
            date_str = m_same.group(1)
            fields["payment_due_date"] = normalize_date_axis(date_str)
            found = True
            break

        # 2) Label alone on one line, date on the next line
        pat_nextline = re.compile(rf"{label}\s*[:\-]?\s*[\r\n]+\s*{date_token_re}", re.IGNORECASE)
        m_next = pat_nextline.search(search_area)
        if m_next:
            date_str = m_next.group(1)
            fields["payment_due_date"] = normalize_date_axis(date_str)
            found = True
            break

        # 3) Label present but date not adjacent — find label position and search small window after it
        m_label = re.search(rf"{label}", search_area, re.IGNORECASE)
        if m_label:
            # look 200 chars after label for a date token
            after = search_area[m_label.end(): m_label.end() + 300]
            m_after = re.search(date_token_re, after, re.IGNORECASE)
            if m_after:
                date_str = m_after.group(1)
                fields["payment_due_date"] = normalize_date_axis(date_str)
                found = True
                break

    # If still not found in top summary, scan the entire document for obvious standalone phrases
    if not found:
        # common standalone patterns where a date follows label or appears near "Due"
        global_patterns = [
            rf"(?:Payment\s+Due\s+Date|Payment\s+Due|Due\s+Date)\s*[:\-]?\s*{date_token_re}",
            rf"(?:Pay\s+by|Last\s+Date\s+for\s+Payment)\s*[:\-]?\s*{date_token_re}",
            # sometimes the statement shows "Due Date" as a separate line like:
            # Due Date
            # 30 Oct 2025
            rf"(?:Due\s+Date)\s*[\r\n]+\s*{date_token_re}",
        ]
        for gp in global_patterns:
            mg = re.search(gp, text, re.IGNORECASE)
            if mg:
                date_str = mg.group(1)
                fields["payment_due_date"] = normalize_date_axis(date_str)
                found = True
                break

    # Final fallback: look for any date token in the top 1k characters that looks like a due-date candidate
    if not found:
        top_small = search_area[:1200]
        candidate_dates = re.findall(date_token_re, top_small, re.IGNORECASE)
        # filter candidate dates to reasonable years (>=2023 and <=2026) when possible
        for cand in candidate_dates:
            norm = normalize_date_axis(cand)
            # accept ISO-like results YYYY-MM-DD or month-only YYYY-MM-01
            if re.match(r"\d{4}-\d{2}-\d{2}", norm) or re.match(r"\d{4}-\d{2}-01", norm):
                # sanity: accept years 2023-2026 as plausible due dates
                year_match = re.match(r"^(\d{4})-", norm)
                if year_match and 2023 <= int(year_match.group(1)) <= 2026:
                    fields["payment_due_date"] = norm
                    found = True
                    break

    # if nothing found, leave payment_due_date as "" (consistent with other empty fields)


    # statement_date: Selected Statement Month OR Statement Date label
    m_sel = re.search(r"Selected\s+Statement\s+Month\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{4})", top, re.IGNORECASE)
    if m_sel:
        fields["statement_date"] = normalize_date_axis(m_sel.group(1))
    else:
        m_sd = re.search(r"Statement\s+Date\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2}\s*'?\d{2,4})", top, re.IGNORECASE)
        if m_sd:
            fields["statement_date"] = normalize_date_axis(m_sd.group(1))

    # billing cycle: Statement period or From ... To ...
    m_cycle = re.search(r"(?:Statement\s*period|Statement\s*Period|Billing\s*Cycle)\s*[:\-]?\s*([A-Za-z0-9\/\-\s,'']+?)\s*(?:to|-)\s*([A-Za-z0-9\/\-\s,'']+?)\b", text, re.IGNORECASE)
    if m_cycle:
        start_raw = m_cycle.group(1).strip()
        end_raw = m_cycle.group(2).strip()
        fields["billing_cycle_start"] = normalize_date_axis(start_raw)
        fields["billing_cycle_end"] = normalize_date_axis(end_raw)
    else:
        # fallback From ... To ...
        m_ft = re.search(r"From\s+([A-Za-z0-9\/\-\s,'']+?)\s+To\s+([A-Za-z0-9\/\-\s,'']+?)\b", text, re.IGNORECASE)
        if m_ft:
            fields["billing_cycle_start"] = normalize_date_axis(m_ft.group(1).strip())
            fields["billing_cycle_end"] = normalize_date_axis(m_ft.group(2).strip())

    # transactions
    txs = extract_transactions_axis(text)
    fields["transactions"] = txs

    # If billing cycle missing, derive from tx dates (earliest/latest)
    if (not fields["billing_cycle_start"] or not fields["billing_cycle_end"]) and txs:
        from datetime import datetime
        valid_dates = []
        for t in txs:
            d = t.get("date") or ""
            if re.match(r"\d{4}-\d{2}-\d{2}", d):
                try:
                    valid_dates.append(datetime.strptime(d, "%Y-%m-%d"))
                except Exception:
                    continue
        if valid_dates:
            valid_dates.sort()
            if not fields["billing_cycle_start"]:
                fields["billing_cycle_start"] = valid_dates[0].strftime("%Y-%m-%d")
            if not fields["billing_cycle_end"]:
                fields["billing_cycle_end"] = valid_dates[-1].strftime("%Y-%m-%d")

    # If statement_date still empty, use billing_cycle_end
    if not fields["statement_date"] and fields["billing_cycle_end"]:
        fields["statement_date"] = fields["billing_cycle_end"]

    return fields




# ---------------  HDFC MILENNIA BANK PARSER ----------------------

import re
from typing import Dict, Any, List
from .utils import find_last4
from datetime import datetime


# -------------------- DATE NORMALIZER --------------------
def normalize_date_hdfc(s: str) -> str:
    """Convert date strings like '14 Oct, 2025' or '15/09/2025' to ISO YYYY-MM-DD."""
    if not s or not s.strip():
        return ""
    s0 = s.strip().replace(",", "").replace("’", "'").replace("‘", "'")
    for fmt in ("%d %b %Y", "%d %B %Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s0, fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return s0


# -------------------- AMOUNT NORMALIZER --------------------
def _hdfc_clean_amount(s: str) -> str:
    s = s.replace(",", "").replace("C", "").replace("`", "").strip()
    s = re.sub(r"^(Rs\.?|INR|₹)\s*", "", s, flags=re.IGNORECASE)
    if re.match(r"^\d+(\.\d{1,2})?$", s):
        if "." not in s:
            s += ".00"
        elif len(s.split(".")[1]) == 1:
            s += "0"
    return "₹" + s


# -------------------- TRANSACTION EXTRACTOR --------------------
def extract_transactions_hdfc(text: str) -> List[Dict[str, Any]]:
    """Extract HDFC Domestic + International transaction rows."""
    txs = []
    block_match = re.search(r"(Domestic Transactions[\s\S]+?)(?:Rewards Program Points|Total Outstanding)", text, re.IGNORECASE)
    if not block_match:
        return txs
    block = block_match.group(1).replace("\r", "\n")

    tx_pattern = re.compile(
        r"(?P<date>\d{1,2}/\d{1,2}/\d{4})\s*\|?\s*(?:\d{1,2}:\d{2}\s*)?"
        r"(?P<desc>[A-Za-z0-9\s\.,'&\-\(\)#/]+?)\s+C\s*(?P<amt>[0-9,]+\.\d{2})",
        re.MULTILINE
    )

    for m in tx_pattern.finditer(block):
        date_iso = normalize_date_hdfc(m.group("date"))
        desc = re.sub(r"^\d+\s+", "", m.group("desc").strip())
        desc = re.sub(r"\s+", " ", desc).strip()
        amt = _hdfc_clean_amount(m.group("amt"))
        tx_type = "Credit" if re.search(r"payment|credit|refund", desc, re.IGNORECASE) else "Debit"
        txs.append({
            "date": date_iso,
            "description": desc,
            "amount": amt,
            "type": tx_type
        })
    return txs


# -------------------- MAIN PARSER --------------------
def parse_hdfc(text: str) -> Dict[str, Any]:
    """Parse HDFC Credit Card statement into structured fields."""
    fields: Dict[str, Any] = {
        "last4": "",
        # "statement_date": "",
        "billing_cycle_start": "",
        "billing_cycle_end": "",
        "payment_due_date": "",
        "total_balance": "",
        "minimum_due": "",
        "transactions": []
    }

    # ---------- LAST 4 DIGITS ----------
    fields["last4"] = find_last4(text) or ""

    import re
    flat_text = None  # Will be created only if needed

        # ---------- helper date token ----------
    date_token_re = re.compile(r"([0-9]{1,2}\s*[A-Za-z]{3,9},?\s*\d{4})", re.IGNORECASE)

    # ---------- STATEMENT DATE (robust, windowed search) ----------
    fields["statement_date"] = ""
    m_label = re.search(r"Statement\s*Date", text, re.IGNORECASE)
    def _find_date_near(text_src: str, start_pos: int, window: int = 150) -> str:
        """Search for first date token within `window` chars after start_pos in text_src."""
        if start_pos >= len(text_src):
            return ""
        snippet = text_src[start_pos:start_pos + window]
        mdate = date_token_re.search(snippet)
        return mdate.group(1) if mdate else ""

    if m_label:
        # search in original text within small window after the label
        cand = _find_date_near(text, m_label.end(), window=180)
        if cand:
            fields["statement_date"] = normalize_date_hdfc(cand)

    # fallback: if not found, try on flattened text
    if not fields["statement_date"]:
        flat_text = " ".join(text.split())
        m_label_flat = re.search(r"Statement\s*Date", flat_text, re.IGNORECASE)
        if m_label_flat:
            cand = _find_date_near(flat_text, m_label_flat.end(), window=200)
            if cand:
                fields["statement_date"] = normalize_date_hdfc(cand)
        # This check ensures we don't accidentally grab a date from the billing period
        # by also searching for the billing period and seeing which comes first.
        # This is a more robust, but complex, check. For this specific case,
        # the regex above is likely sufficient.
        fields["statement_date"] = normalize_date_hdfc(m_stmt.group(1))

    # ---------- BILLING PERIOD ----------
    m_period = re.search(
        r"Billing\s*Period\s*(?:[:\-]?\s*)[\n\r\t ]*([0-9]{1,2}\s*[A-Za-z]{3,9},?\s*\d{4})\s*[-–to]+\s*([0-9]{1,2}\s*[A-Za-z]{3,9},?\s*\d{4})",
        text,
        re.IGNORECASE
    )
    if not m_period:
        # Fallback for flattened text (handles columnar OCR)
        if flat_text is None:
            flat_text = " ".join(text.split())

        ### PROBLEM: Original regex expected date range immediately after label.
        ### SOLUTION: Add '.*?\s*' to non-greedily skip intervening text 
        ### (like the "Statement Date" value) before matching the date range.
        m_period = re.search(
            r"Billing\s*Period\s*.*?\s*([0-9]{1,2}\s*[A-Za-z]{3,9},?\s*\d{4})\s*[-–to]+\s*([0-9]{1,2}\s*[A-Za-z]{3,9},?\s*\d{4})", # <-- MODIFIED
            flat_text,
            re.IGNORECASE
        )

    if m_period:
        fields["billing_cycle_start"] = normalize_date_hdfc(m_period.group(1))
        fields["billing_cycle_end"] = normalize_date_hdfc(m_period.group(2))

    # ---------- TOTAL BALANCE ----------
    m_total = re.search(r"TOTAL\s+AMOUNT\s+DUE\s*(?:\n|:)\s*C?\s*([0-9,]+\.\d{2})", text, re.IGNORECASE)
    if m_total:
        fields["total_balance"] = _hdfc_clean_amount(m_total.group(1))

    # ---------- MINIMUM DUE ----------
    m_min = re.search(r"MINIMUM\s+DUE\s*(?:\n|:)\s*C?\s*([0-9,]+\.\d{2})", text, re.IGNORECASE)
    if m_min:
        fields["minimum_due"] = _hdfc_clean_amount(m_min.group(1))

    # ---------- PAYMENT DUE DATE ----------
    m_due = re.search(
        r"(?:DUE\s+DATE|Payment\s+Due\s+Date)\s*(?:\n|:)?\s*([0-9]{1,2}\s*[A-Za-z]{3,9},?\s*\d{4})",
        text, re.IGNORECASE
    )
    if m_due:
        fields["payment_due_date"] = normalize_date_hdfc(m_due.group(1))

    # ---------- TRANSACTIONS ----------
    fields["transactions"] = extract_transactions_hdfc(text)

    # ---------- Fallback for Statement/Billing dates ----------
    if not fields["statement_date"] and fields["billing_cycle_end"]:
        fields["statement_date"] = fields["billing_cycle_end"]

    return fields

# --------------------------------------------------------------------
                    #  SBI BANK PARSER



# ---------------------- SBI BANK PARSER ----------------------
def parse_sbi(text: str) -> Dict[str, Any]:
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

    # ---- Credit Card Number ----
    # Handles: "Credit Card Number XXXX XXXX XXXX XX46"
    # Works even if there are line breaks between label and digits
    m = re.search(
        r"Credit\s*Card\s*Number[\s:\n\r]*X{2,}\s*X{2,}\s*X{2,}\s*X{2,}\s*X{0,2}(\d{2,4})",
        text,
        re.IGNORECASE,
    )
    if m:
        fields["last4"] = m.group(1).zfill(4)


    # ---- Billing Cycle ----
    m = re.search(r"for\s+Statement\s+Period\s*:\s*([0-9]{1,2}\s*[A-Za-z]{3,}\s*[0-9]{2,4})\s*to\s*([0-9]{1,2}\s*[A-Za-z]{3,}\s*[0-9]{2,4})", text, re.IGNORECASE)
    if m:
        fields["billing_cycle_start"] = normalize_date(m.group(1))
        fields["billing_cycle_end"] = normalize_date(m.group(2))

# ---- Statement Date (robust) ----
    label_stmt = r"Statement\s*Date"
    date_raw = find_date_near_label(text, label_stmt, window_after=200, window_before=40)
    if date_raw:
     fields["statement_date"] = normalize_date(date_raw)

# ---- Payment Due Date (robust) ----
    label_due = r"Payment\s*Due\s*Date"
    date_raw = find_date_near_label(text, label_due, window_after=200, window_before=40)
    if date_raw:
     fields["payment_due_date"] = normalize_date(date_raw)


    # ---- Total Amount Due ----
    m = re.search(r"Total\s*Amount\s*Due.*?([0-9,]+\.\d{2})", text, re.IGNORECASE | re.DOTALL)
    if m:
        fields["total_balance"] = "₹" + m.group(1).replace(",", "")

    # ---- Minimum Amount Due ----
    m = re.search(r"Minimum\s*Amount\s*Due.*?([0-9,]+\.\d{2})", text, re.IGNORECASE | re.DOTALL)
    if m:
        fields["minimum_due"] = "₹" + m.group(1).replace(",", "")

    # ---- Transactions ----
    fields["transactions"] = extract_sbi_transactions(text)

    return fields


def extract_sbi_transactions(text: str):
    """
    Extract SBI transactions — lines typically after 'TRANSACTIONS FOR'
    Example: "30 Sep 25 TPS*PHONEPE WALLET MUMBAI MAH 5,150.00 D"
    """
    txs = []
    start_idx = text.find("TRANSACTIONS FOR")
    if start_idx != -1:
        lines = text[start_idx:].splitlines()
    else:
        lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # ✅ Corrected pattern
        # - captures full description (not just one char)
        # - supports commas in amount
        # - handles optional C/D/M at end
        m = re.match(
            r"(\d{1,2}\s*[A-Za-z]{3}\s*\d{2,4})\s+(.+?)\s+([0-9,]+\.\d{2})\s*[CDM]?$",
            line,
        )

        if m:
            date_str = normalize_date(m.group(1))
            desc = re.sub(r"\s+", " ", m.group(2).strip())
            amt = m.group(3).replace(",", "")
            txs.append(
                {
                    "date": date_str,
                    "description": desc,
                    "amount": amt,
                }
            )

    return txs




# --------------------# Generic transaction extractor (used by Kotak, ICICI)



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
