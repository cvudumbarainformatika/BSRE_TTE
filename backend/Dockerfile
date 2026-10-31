FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (compiler, libpq dev, dan LibreOffice headless untuk konversi Word/EPUB ke PDF)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    libreoffice-writer-nogui \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Buat direktori storage
RUN mkdir -p /app/storage/app/documents /app/storage/app/qr_codes /app/storage/app/temp /app/storage/logs

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
