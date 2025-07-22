FROM python:3.11-slim

# 필수 빌드 도구 및 distutils 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-distutils \
        gcc \
        build-essential \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

# pip, setuptools, wheel 최신화 및 requirements.txt 설치
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]