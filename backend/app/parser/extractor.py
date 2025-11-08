# backend/app/parser/extractor.py
import io
import os
from pypdf import PdfReader
from .utils import text_stats
from .bank_parsers import detect_bank_and_parse
from pdf2image import convert_from_bytes
import pytesseract
from typing import Dict, Any

# ✅ Explicit path for Tesseract OCR (Windows)
TESSERACT_PATH = r"C:\Users\Deepak Mahto\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print(f"🧠 Using Tesseract from: {TESSERACT_PATH}")
else:
    print(f"⚠️ Warning: Tesseract not found at {TESSERACT_PATH}. OCR fallback may fail.")

# ✅ Explicit Poppler path for Windows
POPLER_PATH = r"C:\Program Files\poppler-25.07.0\Library\bin"

OCR_MIN_TEXT_LEN = 200  # if extracted text is smaller than this, do OCR fallback


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Try to extract text using pypdf. Return concatenated text.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        texts = []
        for page in reader.pages:
            try:
                t = page.extract_text() or ""
            except Exception as e:
                print(f"⚠️ Text extraction failed on a page: {e}")
                t = ""
            texts.append(t)
        return "\n".join(texts).strip()
    except Exception as e:
        print(f"❌ Failed to read PDF with PyPDF: {e}")
        return ""


def ocr_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Convert pdf pages to images and OCR them with pytesseract.
    If OCR fails, return an empty string (do not crash).
    """
    try:
        if not os.path.exists(POPLER_PATH):
            print(f"⚠️ Poppler not found at {POPLER_PATH}. OCR may fail.")

        images = convert_from_bytes(pdf_bytes, dpi=200, poppler_path=POPLER_PATH)

        ocr_texts = []
        for i, img in enumerate(images):
            try:
                txt = pytesseract.image_to_string(img)
                print(f"✅ OCR done for page {i + 1}, {len(txt)} chars")
                ocr_texts.append(txt)
            except Exception as e:
                print(f"⚠️ OCR failed on page {i + 1}: {e}")

        return "\n".join(ocr_texts).strip()

    except Exception as e:
        print(f"⚠️ OCR fallback failed entirely: {e}")
        return ""


def parse_pdf_bytes(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Returns: { "bank": bank_name, "fields": {...} }
    """
    text = extract_text_from_pdf_bytes(pdf_bytes)

    # If the text looks too small, try OCR fallback
    if text_stats(text)["char_count"] < OCR_MIN_TEXT_LEN:
        print("🧩 Text too short; attempting OCR fallback...")
        ocr_text = ocr_pdf_bytes(pdf_bytes)
        # Prefer OCR text if it’s longer
        if len(ocr_text) > len(text):
            text = ocr_text
            print("✅ OCR text used for parsing.")
        else:
            print("⚠️ OCR text was not longer than extracted text. Using original text.")

    # 🧩 Debug: print first few thousand characters
    print("========== RAW EXTRACTED TEXT ==========")
    print(text[:2000])
    print("========================================")

    try:
        parsed = detect_bank_and_parse(text)
    except Exception as e:
        print(f"❌ Parsing error inside detect_bank_and_parse: {e}")
        parsed = {"bank": "UNKNOWN", "fields": {}}

    return parsed
