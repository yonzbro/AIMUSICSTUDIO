FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    python3-dev \
    cmake \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Pre-install Cython (needed for pyworld/fairseq)
RUN pip install --no-cache-dir Cython

# Install PyTorch with CUDA 11.8 support
RUN pip install --no-cache-dir --retries 10 --timeout 1000 \
    torch==2.1.2 \
    torchaudio==2.1.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --retries 10 --timeout 1000 -r requirements.txt

# Create directories for models and outputs
RUN mkdir -p /app/models/pretrained /app/models/checkpoints /app/outputs /app/voice_profiles

# Copy source code
COPY . .

# Clone RVC core components (minimal) at the end to avoid cache invalidation
RUN git clone --depth 1 https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git /tmp/rvc && \
    mkdir -p /app/configs /app/tools /app/assets && \
    cp -rn /tmp/rvc/infer /app/ && \
    (cp -rn /tmp/rvc/lib /app/ || echo "No lib") && \
    (cp -rn /tmp/rvc/configs/* /app/configs/ || echo "No configs") && \
    (cp -rn /tmp/rvc/tools/* /app/tools/ || echo "No tools") && \
    (cp -rn /tmp/rvc/assets/* /app/assets/ || echo "No assets") && \
    rm -rf /tmp/rvc

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

EXPOSE 8006

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
