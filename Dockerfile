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

WORKDIR /app/src

EXPOSE 8080

# Railway 강제 시작 명령어 - 캐시 무시
CMD ["python", "-c", "import uvicorn; import sys; sys.path.insert(0, '/app/src'); uvicorn.run('app:app', host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 8080)))"]