# backend/Dockerfile

# Dockerfile for the backend service
FROM python:3.12 AS build-flask


RUN apt-get update && apt-get install -y \
        build-essential \
        cmake \
        python3-dev \
        ninja-build

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . .

# Expose the port your Flask app will run on (default is 5000)
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]