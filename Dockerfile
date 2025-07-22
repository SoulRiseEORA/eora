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

EXPOSE 8000

CMD sh -c "uvicorn app:app --host=0.0.0.0 --port=${PORT}"