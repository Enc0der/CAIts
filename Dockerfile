FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY config.json .
COPY app.py .
COPY requirements.txt .
COPY data/ ./data/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
