# Dockerfile

FROM python:3.12

WORKDIR /app

# Install tzdata for timezone support for logging
RUN apt-get update \
  && apt-get install -y --no-install-recommends tzdata \
  && rm -rf /var/lib/apt/lists/*

# Copy dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code, configs, and data
COPY app/ ./app/
COPY configs/ ./configs/
COPY data/ ./data/

# Prepare output dirs
RUN mkdir -p data/plaintext data/processed logs

# Expose FastAPI port
EXPOSE 8000

# Set ENV Variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    SETTINGS_PATH=/app/configs/settings.yaml \
    LOGGING_CONFIG=/app/configs/logging_config.yaml

# Launch sequence: parse → chunk → serve
CMD python -m app.services.html_parser \
 && python -m app.services.chunker \
 && uvicorn app.main:app --host 0.0.0.0 --port 8000
