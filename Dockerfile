FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 1. Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip

# 2. Install "Heavy" dependencies individually to cache them
# Based on your logs, Streamlit and Jupyter are the ones causing the timeout
RUN pip install --no-cache-dir streamlit jupyter insightface

# 3. Now install the rest of the requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --retries 10 --default-timeout=1000 -r requirements.txt
    
# Copy application code
COPY . .

# Copy and set permissions for entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir -p storage/faces storage/models

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]