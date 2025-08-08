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

# Railway 완벽 시작 - 환경변수 안전 처리
CMD ["python", "railway_start.py"]