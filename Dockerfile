# Use an official Python runtime as the base image
FROM python:3.12.6-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the backend folder to the working directory
COPY backend/ /app/backend/

# Copy the .env file to the container
COPY .env /app/.env

# Install the dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Expose port 8080 inside the container (to match the FastAPI configuration)
EXPOSE 8080

# Set environment variable for FastAPI to use the .env file
ENV ENV_PATH=/app/.env

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
