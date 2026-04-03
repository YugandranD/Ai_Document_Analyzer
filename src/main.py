"""
AI-Powered Document Analysis & Extraction API

FastAPI application that accepts base64-encoded documents (PDF, DOCX, images),
extracts text content, and returns AI-generated summaries, entities, and sentiment.
"""

import logging
import time

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from src.config import API_KEY
from src.extractors import decode_base64, extract_text
from src.analyzer import analyze_document

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Document Analysis API",
    description="AI-powered document processing: extract, analyse and summarise content from PDF, DOCX & images.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class DocumentRequest(BaseModel):
    fileName: str = Field(..., description="Uploaded file name")
    fileType: str = Field(..., description="pdf / docx / image")
    fileBase64: str = Field(..., description="Base64-encoded file content")


class EntitiesResponse(BaseModel):
    names: list[str] = []
    dates: list[str] = []
    organizations: list[str] = []
    amounts: list[str] = []


class DocumentResponse(BaseModel):
    status: str = "success"
    fileName: str
    summary: str
    entities: EntitiesResponse
    sentiment: str


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------
def verify_api_key(x_api_key: str = Header(None)):
    """Validate the x-api-key header."""
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail={"status": "error", "message": "Unauthorized – invalid or missing API key"},
        )
    return x_api_key


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "service": "Document Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post(
    "/api/document-analyze",
    response_model=DocumentResponse,
    responses={401: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
async def analyze_document_endpoint(
    body: DocumentRequest,
    x_api_key: str = Header(None),
):
    """
    Analyze a document: extract text, generate summary, extract entities,
    and determine sentiment.

    Requires `x-api-key` header for authentication.
    """

    # --- Auth ---
    verify_api_key(x_api_key)

    # --- Validate file type ---
    allowed_types = {"pdf", "docx", "doc", "image", "img", "png", "jpg", "jpeg", "tiff", "bmp"}
    file_type = body.fileType.lower().strip()
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": f"Unsupported fileType: {body.fileType}"},
        )

    # --- Process ---
    start = time.time()
    try:
        logger.info(f"Processing {body.fileName} (type={file_type})")

        # 1. Decode base64
        file_bytes = decode_base64(body.fileBase64)
        logger.info(f"Decoded {len(file_bytes)} bytes")

        # 2. Extract text
        extracted_text = extract_text(file_type, file_bytes)
        logger.info(f"Extracted {len(extracted_text)} chars of text")

        if not extracted_text.strip():
            raise ValueError("No text could be extracted from the document")

        # 3. AI analysis
        analysis = analyze_document(extracted_text)
        elapsed = round(time.time() - start, 2)
        logger.info(f"Analysis complete in {elapsed}s")

        return DocumentResponse(
            status="success",
            fileName=body.fileName,
            summary=analysis["summary"],
            entities=EntitiesResponse(**analysis["entities"]),
            sentiment=analysis["sentiment"],
        )

    except ValueError as e:
        logger.error(f"Extraction error: {e}")
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": f"Processing failed: {str(e)}"},
        )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    from src.config import HOST, PORT

    uvicorn.run("src.main:app", host=HOST, port=PORT, reload=True)
