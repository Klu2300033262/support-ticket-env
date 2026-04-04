# Use Python 3.11 slim as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Force specific OpenEnv version and break all caching
ARG OPENENV_VERSION=0.1.0
RUN pip install --upgrade pip

# Install dependencies with explicit version to avoid cache conflicts
RUN pip install --no-cache-dir "openenv-core==${OPENENV_VERSION}" fastapi>=0.115.0 uvicorn>=0.24.0 sqlalchemy aiosqlite

# Copy the entire support_ticket_env source into the container
COPY support_ticket_env/ ./

# Install the package in development mode
RUN pip install -e .

# Expose port 7860 (required by HF Spaces)
EXPOSE 7860

# Set PYTHONPATH to ensure imports identify support_ticket_env as a module if needed
ENV PYTHONPATH="/app"

# Run the FastAPI server using uvicorn on port 7860
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
