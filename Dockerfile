# Dockerfile for SIA Project
# Supports both CLI and API usage

FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Default command (can be overridden)
# Use: docker run ... python sia_cli.py --help
CMD ["python", "sia_cli.py"]