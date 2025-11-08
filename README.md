# 🧾 Kotak Credit Card Statement Parser (Windows Setup)
🧰 Prerequisites

Python 3.10+ installed
Tesseract OCR → Download
→ Install to: C:\Program Files\Tesseract-OCR\tesseract.exe
Poppler for Windows → Download
→ Extract to: C:\Program Files\poppler-25.07.0\Library\bin
Kotak credit card statement PDF file (e.g., kotakbank.pdf)

# ⚙️ 1. Create & activate virtual environment
cd C:\Users\Deepak Mahto\Downloads\sureassignement\backend
python -m venv .venv
.venv\Scripts\Activate.ps1

# 📦 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

(If you get missing package errors later, install manually:
pip install fastapi uvicorn pypdf pdf2image pillow pytesseract python-multipart python-dateutil)

# 🧠 3. Check tool paths in extractor.py

Make sure these lines are correct:

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPLER_PATH = r"C:\Program Files\poppler-25.07.0\Library\bin"

# 🚀 4. Run the backend
uvicorn app.main:app --reload --port 8000


You’ll see:

🧠 Using Tesseract from: C:\Program Files\Tesseract-OCR\tesseract.exe
INFO: Uvicorn running on http://127.0.0.1:8000

# 🌐 5. Test it

Open browser → http://localhost:8000/docs

Click POST /parse → Try it out

Upload your kotakbank.pdf

Click Execute

✅ You’ll see JSON output like:

{
  "success": true,
  "bank": "KOTAK",
  "fields": {
    "last4": "8253",
    "payment_due_date": "2025-11-07",
    "total_balance": "2253.00"
  }
}

# 🧩 6. Common fixes
Issue	Fix
uvicorn not recognized	Run pip install uvicorn
No module named pypdf	Run pip install pypdf
Form data requires python-multipart	Run pip install python-multipart
Poppler not found	Fix POPLER_PATH
Tesseract not found	Fix TESSERACT_PATH
✅ Done!

Your API runs at
👉 http://localhost:8000/docs

Upload a Kotak PDF and view extracted statement details.