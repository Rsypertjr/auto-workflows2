# --- STAGE 1: BUILD DEPENDENCIES ---
FROM python:3.11-slim AS builder

WORKDIR /app 

# Install native system build dependencies needed for packages like psutil or asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# FIX: Explicitly target the system package tree, bypassing the private /root/ user directory
RUN pip install --no-cache-dir --target=/usr/local/lib/python3.11/site-packages -r requirements.txt
RUN pip install --no-cache-dir --no-warn-script-location celery


# --- STAGE 2:  FINAL RUNTIME ENVIRONMENT ---
FROM python:3.11-slim AS runner

WORKDIR /app 

# Copies your local backend folder contents (including credentials.json) straight to /app
COPY . .

#  Install minimal runtime library dependencies required by PostgreSQL/system drivers 
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \ 
    && rm -rf /var/lib/apt/lists/*


# Copy system packages cleanly so they match your non-root container constraints
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .


# Create a secure, non-privileged system application user matching your UID/GID parameters
RUN groupadd -g 1000 appuser && useradd -r -u 1000 -g appuser appuser
RUN chown -R appuser:appuser /app

# Switch to the non-root user so all application processes launch safely
USER appuser

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