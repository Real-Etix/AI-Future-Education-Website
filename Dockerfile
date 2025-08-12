# backend/Dockerfile

# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3-dev \
    ninja-build \
    g++ \
    clang \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY backend/. .
COPY frontend/dist .

# Expose the port your Flask app will run on (default is 5000)
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]