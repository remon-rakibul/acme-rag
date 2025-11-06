FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and clean up in same layer to save space
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip

# Copy and install requirements with aggressive cleanup
COPY requirements.txt .
RUN pip install --no-cache-dir --no-warn-script-location -r requirements.txt \
    && pip cache purge \
    && rm -rf /root/.cache/pip \
    && rm -rf /root/.cache/huggingface \
    && find /usr/local/lib/python3.11/site-packages -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/*

# Copy application code
COPY app/ ./app/

# Create data directory
RUN mkdir -p /app/data

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV API_KEY=acme-ai-secret-key-2025

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

