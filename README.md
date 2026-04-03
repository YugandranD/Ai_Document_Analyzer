# Data Extraction API

## Description
AI-powered document processing system that extracts, analyses, and summarises content from PDF, DOCX, and image files. The system uses Groq (LLaMA 3) for intelligent analysis, Tesseract OCR for image text extraction, and provides a clean REST API for document processing.

## Tech Stack
- **Language/Framework:** Python 3.11+ / FastAPI
- **OCR:** Tesseract (pytesseract)
- **AI/LLM:** Groq LLaMA 3 (via `groq` python SDK)
- **Async Processing:** Celery + Redis
- **PDF Extraction:** PyPDF2
- **DOCX Extraction:** python-docx
- **Image Processing:** Pillow

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd Guvi_Ai
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR
- **Windows:** Download from https://github.com/UB-Mannheim/tesseract/wiki and install
- **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
- **macOS:** `brew install tesseract`

### 5. Set environment variables
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 6. Run the application
```bash
# Direct run
uvicorn src.main:app --host 0.0.0.0 --port 8000

# Or using Python
python -m src.main
```

### 7. (Optional) Start Celery worker for async processing
```bash
celery -A src.celery_worker.celery_app worker --loglevel=info
```

## API Documentation

### Endpoint
```
POST /api/document-analyze
```

### Authentication
All requests require an `x-api-key` header:
```
x-api-key: sk_track2_987654321
```

### Request Body
| Field | Type | Description |
|-------|------|-------------|
| fileName | string | Uploaded file name |
| fileType | string | `pdf` / `docx` / `image` |
| fileBase64 | string | Base64-encoded file content |

### Example cURL Request
```bash
curl -X POST https://your-domain.com/api/document-analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_track2_987654321" \
  -d '{
    "fileName": "sample1.pdf",
    "fileType": "pdf",
    "fileBase64": "JVBERi0xLjQK..."
  }'
```

### Success Response
```json
{
  "status": "success",
  "fileName": "sample1.pdf",
  "summary": "This document is an invoice issued by ABC Pvt Ltd...",
  "entities": {
    "names": ["Ravi Kumar"],
    "dates": ["10 March 2026"],
    "organizations": ["ABC Pvt Ltd"],
    "amounts": ["₹10,000"]
  },
  "sentiment": "Neutral"
}
```

### Error Response (401 Unauthorized)
```json
{
  "status": "error",
  "message": "Unauthorized – invalid or missing API key"
}
```

## Approach

### Text Extraction Strategy
- **PDF:** Uses PyPDF2 to extract text layers. Falls back to OCR via Tesseract for scanned/image-based PDF pages.
- **DOCX:** Uses python-docx to extract paragraphs and table content with layout preservation.
- **Images:** Uses Tesseract OCR (pytesseract) with Pillow for image preprocessing.

### AI Analysis
- **Summarisation:** Groq (LLaMA 3) generates a concise 1-3 sentence summary capturing key information.
- **Entity Extraction:** The LLM identifies and categorises entities into names, dates, organisations, and monetary amounts.
- **Sentiment Analysis:** The LLM classifies overall document sentiment as Positive, Negative, or Neutral based on content tone.

### Fallback Mechanism
If the AI model is unavailable, the system falls back to regex-based extraction for dates, amounts, and basic text truncation for summaries.

## AI Tools Used
- **Groq API (LLaMA 3 8B):** Used as the core language model to intelligently read extracted text, summarize context, extract complex entities (names, dates, organizations, amounts), and determine overall sentiment.
- **Tesseract OCR:** Used as an intelligent AI-driven neural net backend for Optical Character Recognition to extract text layers from images and rasterized PDF pages.
- **Antigravity AI Assistant:** Used as a pair-programming coding assistant to help build the FASTAPI backend, implement Groq models, design the deployment pipeline, and write this documentation.

## Project Structure
```
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── Procfile                  # Deployment config
└── src/
    ├── __init__.py
    ├── main.py               # FastAPI application & routes
    ├── config.py             # Configuration from env vars
    ├── extractors.py         # Text extraction (PDF, DOCX, OCR)
    ├── analyzer.py           # AI-powered analysis (Gemini)
    └── celery_worker.py      # Async task processing
```

## Live API
- **URL:** `https://your-domain.com`
- **Docs:** `https://your-domain.com/docs`
