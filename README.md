💳 Credit Card Statement Parser

A developer-friendly project that lets users upload PDF credit card statements (Kotak, ICICI, Axis, HDFC, SBI, etc.), extract structured financial data, and display results in a modern UI.
It demonstrates PDF parsing → regex/heuristics → optional OCR → structured JSON output.

🚀 Project Summary

This project provides a clean and intuitive interface to:
Upload a credit card statement (PDF)
Send it to a FastAPI backend (/parse endpoint)
Extract & display key details:
Last 4 digits of card
Statement date
Billing cycle
Payment due date
Total balance & minimum due
Transaction list

🔧 Tech Stack

Frontend

⚛️ React (Vite)
🎨 Tailwind CSS
💎 Lucide Icons (lucide-react)
🌐 Axios (HTTP client)

Backend (assumed)
🚀 FastAPI (Python)
📄 PDF parsing libraries
pdfminer.six, PyMuPDF (fitz), or pdfplumber
🔍 (Optional) OCR
Tesseract / pytesseract or a cloud OCR API
🗄️ (Optional) Database
SQLite / PostgreSQL for storing parsed results
Dev Tooling
Node.js + npm / yarn / pnpm
Vite (frontend build tool)
FastAPI (backend framework)

📁 Project Flow & Architecture
1️⃣ User selects PDF
The user uploads or drags a credit card statement into the UI.
2️⃣ Frontend sends file
UploadForm constructs a FormData object and sends a POST request to:
POST /parse
Content-Type: multipart/form-data
3️⃣ Backend receives file
FastAPI:
Saves or streams the PDF
Extracts text via:
PDF text parser
OCR fallback if text extraction fails
Normalizes text (clean spacing, currency, date formats)
Uses regex / rules / ML-based parsing to extract fields and transactions
4️⃣ Backend returns structured JSON
Example:{
"success": true,
"bank": "HDFC",
"fields": {
"last4": "1234",
"statement_date": "2025-10-31",
"billing_cycle_start": "2025-10-01",
"billing_cycle_end": "2025-10-31",
"payment_due_date": "2025-11-15",
"total_balance": "₹12,345.67",
"minimum_due": "₹1,234.00",
"transactions": [
{ "date": "2025-10-05", "description": "Amazon IN", "amount": "1,599.00" },
{ "date": "2025-10-12", "description": "Zomato", "amount": "349.00" }
]
}
}
5️⃣ Frontend displays parsed data
The React app renders a clean ResultCard summarizing statement details and transaction tables.
6️⃣ (Optional) Post-processing / Storage
The backend may persist results, send notifications, or integrate with accounting systems.

📦 File Structure
src/
main.jsx
App.jsx
index.css
components/
UploadForm.jsx
ResultCard.jsx
Button.jsx
FileInput.jsx

⚙️ Setup & Run (Frontend)
🧩 Install dependencies

# Using npm

npm install

# or yarn

yarn

# or pnpm

pnpm install
🌍 Environment setup
Create a .env file at the project root:
VITE_API_BASE=http://127.0.0.1:8000
🧠 Run development server
npm run dev

# or

yarn dev

# or

pnpm dev

🏗️ Build for production
npm run build

# Serve the /dist folder via your web server

🛠️ Backend API Contract
Endpoint:
POST /parse

Headers:
Content-Type: multipart/form-data
Form field:
file — PDF statement file
Response (Success):{
"success": true,
"bank": "Axis Bank",
"fields": { ... }
}
Response (Error):{
"success": false,
"error": "Description of error"
}

📈 Suggested Improvements (Roadmap)
🧠 OCR fallback for scanned statements
🤖 ML/NLP-based extraction for more robust detection
🧾 CSV / Excel export of transactions
🔐 User authentication + history dashboard
🔄 Async job queue for long-running OCR/parsing
🧪 Admin mode for debugging regex extraction rules
