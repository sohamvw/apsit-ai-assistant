FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for ML libs
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only backend
COPY api ./api

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r api/requirements.txt

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
