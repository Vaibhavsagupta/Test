FROM python:3.10-slim

# Install system dependencies for FAISS and other libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install CPU-only torch to save massive disk space (no CUDA needed)
COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8000

# Command to run the application (Integrated Task 1 & 2)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
