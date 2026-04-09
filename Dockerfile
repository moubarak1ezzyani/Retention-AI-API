# 1. Use the official lightweight Python image
FROM python:3.11-slim

# 2. Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# PYTHONUNBUFFERED: Ensures console output is not buffered by Docker (makes logs real-time)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /code

# 4. Install system dependencies required for PostgreSQL (psycopg2) and ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy the requirements file first (Leverages Docker layer caching)
COPY requirements.txt /code/

# 6. Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Copy the application code and models into the container
# We explicitly copy what is needed to keep the container clean
COPY ./app /code/app
COPY ./models /code/models

# 8. Expose the port Uvicorn will run on
EXPOSE 8000

# 9. Command to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]