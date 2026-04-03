FROM python:3.11-slim

# Install Tesseract OCR
RUN apt-get update && \
    apt-get install -y --no-install-recommends tesseract-ocr && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set environment variables
ENV TESSERACT_PATH=/usr/bin/tesseract
ENV HOST=0.0.0.0

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
