"""
AI-powered document analysis using Google Gemini.
Handles summarisation, entity extraction, and sentiment analysis.
"""

import json
import logging
import re

import os
from groq import Groq

from src.config import GROQ_API_KEY

logger = logging.getLogger(__name__)

# Configure Groq
client = Groq(api_key=GROQ_API_KEY)

ANALYSIS_PROMPT = """You are an expert document analyst. Analyze the following document text and return a JSON object with exactly these fields:

1. "summary": A concise 1-3 sentence summary of the document content. Capture the key purpose, parties involved, dates, and amounts if present.

2. "entities": An object with these arrays:
   - "names": All person names mentioned (e.g., "Ravi Kumar", "John Smith")
   - "dates": All dates mentioned in their original format (e.g., "10 March 2026", "2024-01-15")
   - "organizations": All company/organization names (e.g., "ABC Pvt Ltd", "Google")
   - "amounts": All monetary amounts with currency symbols (e.g., "₹10,000", "$5,000")

3. "sentiment": The overall sentiment of the document. Must be exactly one of: "Positive", "Negative", or "Neutral"

Rules:
- Extract ALL entities, not just the first few
- Keep the summary factual and concise
- For sentiment: invoices, reports, and factual documents are "Neutral"; complaints and negative reviews are "Negative"; praise and positive feedback are "Positive"
- Return ONLY valid JSON, no markdown code blocks, no extra text

Document text:
---
{text}
---

Return only the JSON object:"""


def analyze_document(text: str) -> dict:
    """
    Use Gemini to analyze extracted document text.

    Args:
        text: The extracted text from the document

    Returns:
        Dict with keys: summary, entities, sentiment
    """
    if not text or not text.strip():
        return {
            "summary": "The document appears to be empty or contains no extractable text.",
            "entities": {
                "names": [],
                "dates": [],
                "organizations": [],
                "amounts": [],
            },
            "sentiment": "Neutral",
        }

    # Truncate very long texts to stay within token limits
    max_chars = 30000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n... [truncated]"

    prompt = ANALYSIS_PROMPT.format(text=text)

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.1,
            max_tokens=2048,
            response_format={"type": "json_object"},
        )

        raw = completion.choices[0].message.content.strip()
        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        result = json.loads(raw)

        # Validate and normalise structure
        return _validate_result(result)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Groq response as JSON: {e}\nRaw: {raw}")
        return _fallback_analysis(text)
    except Exception as e:
        logger.error(f"Groq analysis failed: {e}")
        return _fallback_analysis(text)


def _validate_result(result: dict) -> dict:
    """Ensure the AI result has the expected structure."""
    validated = {
        "summary": result.get("summary", ""),
        "entities": {
            "names": result.get("entities", {}).get("names", []),
            "dates": result.get("entities", {}).get("dates", []),
            "organizations": result.get("entities", {}).get("organizations", []),
            "amounts": result.get("entities", {}).get("amounts", []),
        },
        "sentiment": result.get("sentiment", "Neutral"),
    }

    # Normalise sentiment
    sentiment = validated["sentiment"].strip().capitalize()
    if sentiment not in ("Positive", "Negative", "Neutral"):
        validated["sentiment"] = "Neutral"
    else:
        validated["sentiment"] = sentiment

    # Ensure all entity lists contain strings
    for key in validated["entities"]:
        validated["entities"][key] = [
            str(item) for item in validated["entities"][key] if item
        ]

    return validated


def _fallback_analysis(text: str) -> dict:
    """Basic regex-based fallback when AI is unavailable."""
    import re as _re

    # Simple entity extraction via patterns
    names = []
    dates = _re.findall(
        r"\b\d{1,2}[\s/\-]\w+[\s/\-]\d{2,4}\b|\b\w+\s\d{1,2},?\s\d{4}\b", text
    )
    amounts = _re.findall(
        r"[₹$€£¥]\s?[\d,]+(?:\.\d{2})?|\b\d[\d,]*(?:\.\d{2})?\s?(?:USD|INR|EUR|GBP)\b",
        text,
    )

    return {
        "summary": text[:300].strip() + ("..." if len(text) > 300 else ""),
        "entities": {
            "names": names,
            "dates": dates,
            "organizations": [],
            "amounts": amounts,
        },
        "sentiment": "Neutral",
    }
