# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install all system dependencies required by OpenCV and other ML libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY functions-python/requirements.txt .

# Install the Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY functions-python/ .

# This line is not used by Cloud Functions but is good practice
CMD ["python", "main.py"]