# Use Python 3.11 slim as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Ensure latest pip
RUN pip install --upgrade pip

# Install runtime dependencies first (for better layer caching)
RUN pip install --no-cache-dir \
    "openenv-core>=0.1.0" \
    "openai>=1.0.0" \
    "python-dotenv>=1.0.0" \
    "fastapi>=0.115.0" \
    "uvicorn>=0.24.0" \
    "sqlalchemy>=2.0.0" \
    "aiosqlite>=0.19.0"

# Copy the source code
COPY server/ ./server/
COPY models.py ./models.py
COPY client.py ./client.py
COPY inference.py ./inference.py
COPY tasks.py ./tasks.py
COPY frontend/ ./frontend/

# Expose port 8000
EXPOSE 8000

# Set PYTHONPATH so Python can resolve top-level modules
ENV PYTHONPATH="/app"

# Add health check for openenv 
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI server using uvicorn on port 8000
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
