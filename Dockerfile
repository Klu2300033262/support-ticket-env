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

# Copy the support_ticket_env source as a proper subdirectory
# (keeps the package namespace intact for imports like: from support_ticket_env.models import ...)
COPY support_ticket_env/ ./support_ticket_env/

# Copy inference and task definition scripts (used by the evaluator)
COPY inference.py ./inference.py
COPY tasks.py ./tasks.py

# Copy frontend assets
COPY frontend/ ./frontend/

# Install the package in development mode from the subdirectory
RUN pip install --no-cache-dir -e ./support_ticket_env/

# Expose port 7860 (required by HF Spaces)
EXPOSE 7860

# Set PYTHONPATH so Python can resolve top-level modules (tasks.py, inference.py)
ENV PYTHONPATH="/app"

# Run the FastAPI server using uvicorn on port 7860
CMD ["uvicorn", "support_ticket_env.server.app:app", "--host", "0.0.0.0", "--port", "7860"]
