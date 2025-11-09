# backend/app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.parser.extractor import parse_pdf_bytes
import uvicorn

app = FastAPI(title="Credit Card Statement Parser")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to ["http://localhost:5173"] later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/parse")
async def parse(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    contents = await file.read()
    result = parse_pdf_bytes(contents)

    bank = result.get("bank", "").upper()
    if bank not in ["KOTAK", "ICICI", "AXIS", "HDFC", "SBI"]:
        return JSONResponse(
            status_code=400,
            content={"error": "Only Kotak, ICICI, Axis, HDFC, and SBI Bank statements are supported."}
        )


    return {"success": True, "bank": bank, "fields": result.get("fields")}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

