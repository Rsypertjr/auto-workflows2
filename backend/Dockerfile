# --- STAGE 1: BUILD DEPENDENCIES ---
FROM python:3.11-slim AS builder

WORKDIR /app 

# Install native system build dependencies needed for packages like psutil or asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# Copy and install python dependencies into a local directory
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- STAGE 2:  FINAL RUNTIME ENVIRONMENT ---
FROM python:3.11-slim AS runner

WORKDIR /app 

#  Install minimal runtime library dependencies required by PostgreSQL/system drivers 
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \ 
    && rm -rf /var/lib/apt/lists/*

# Copy the pre-built packages from the builder stage over to this clean image
COPY --from=builder /root/.local /root/.local
COPY . .


# Install Google API client libraries
RUN pip install --no-cache-dir google-api-python-client google-auth-httplib2 google-auth-oauthlib

# FIX: Explicitly mount the user local binaries to the system binary PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Document that the app container communicates exclusively on port 8000
EXPOSE 8000

# Run using Uvicorn optimized for container archetectures:
# - '--host 0.0.0.0' binds to all network interfaces inside the isolated container
# - '--workers 4' enables process concurrency to handle heavier traffic loads 
# FIX: Execute via the Python module flag (-m) to safely find uvicorn if PATH fails
CMD ["python", "-m", "uvicorn", "app.main:app","--reload","--host", "0.0.0.0", "--port", "8000", "--workers", "4"]