# Use Python 3.11 slim as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Ensure latest pip and clean cache
RUN pip install --upgrade pip && rm -rf /root/.cache/pip

# Copy source first to ensure fresh context
COPY support_ticket_env/ ./

# Install the package first (this installs dependencies)
RUN pip install -e .

# Expose port 7860 (required by HF Spaces)
EXPOSE 7860

# Set PYTHONPATH to ensure imports identify support_ticket_env as a module if needed
ENV PYTHONPATH="/app"

# Run the FastAPI server using uvicorn on port 7860
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
