# Use a specific, stable Python version as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# The key fix: Install all system-level dependencies for C++ compilation and headless computer vision
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY the requirements file first to leverage Docker layer caching
COPY functions-python/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your function's code
COPY functions-python/ .

# === THIS IS THE CRITICAL FIX ===
# Starts the web server that Cloud Run expects, listening on the correct port.
CMD exec functions-framework --target=run_prediction --port=${PORT:-8080}
# =================================