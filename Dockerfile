FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt-get/lists/*

RUN pip install --no-cache-dir uvicorn fastapi

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main_app:app", "--host", "0.0.0.0", "--port", "8000"]