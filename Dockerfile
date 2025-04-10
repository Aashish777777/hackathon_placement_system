# Use ubuntu:22.04 as base image
FROM ubuntu:22.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file (if any)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install pandas and flask (if not in requirements.txt)
RUN pip3 install pandas flask

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["python3", "app.py"]