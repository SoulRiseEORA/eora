FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-distutils \
    gcc \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

WORKDIR /app

EXPOSE 8080

# Railway 강제 시작 - uvicorn 우선 사용 (WORKDIR /app 기준)
CMD ["sh", "-c", "uvicorn src.app:app --host 0.0.0.0 --port ${PORT:-8080} || python railway_safe_server.py"]