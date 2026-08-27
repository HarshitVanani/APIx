FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for headless browsers
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries and system libraries
RUN playwright install --with-deps chromium

# Copy all backend application code
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]