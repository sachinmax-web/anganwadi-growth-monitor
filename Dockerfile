# =============================================================
# Task 3 — Dockerfile
# Dependencies are installed BEFORE source is copied so that a
# code-only change does not trigger a full pip reinstall.
# No secrets or environment-specific values are baked in.
# =============================================================

FROM python:3.11-slim

# 1. System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Install Python dependencies first (layer is cached on code changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy application source
COPY . .

# 4. Runtime configuration — supplied via env vars at run time, never hard-coded
ENV DB_PATH=/app/data/anganwadi.db

# 5. Ensure data directory exists
RUN mkdir -p /app/data

# 6. Default command
CMD ["python", "main.py"]
