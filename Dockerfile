# Use Python 3.11 slim as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Ensure latest pip
RUN pip install --upgrade pip

# Force cache invalidation with timestamp and checksum
ARG BUILD_DATE=2026-04-04-17-30-00
ADD support_ticket_env/server/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

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
