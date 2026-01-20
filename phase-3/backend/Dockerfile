# Hugging Face Spaces Dockerfile for Todo AI Chatbot Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy phase-3 backend files to /app
COPY phase-3/backend/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH so 'src' module can be found
ENV PYTHONPATH=/app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose Hugging Face Spaces port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run application on Hugging Face Spaces port
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]