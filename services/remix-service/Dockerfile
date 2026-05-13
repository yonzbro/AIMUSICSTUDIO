FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Python kurulumu
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY requirements.txt .
# Install PyTorch with CUDA first, then remaining deps (torchcodec needs standard PyPI)
RUN pip install --no-cache-dir torch>=2.0.0 torchaudio>=2.0.0 --extra-index-url https://download.pytorch.org/whl/cu121 \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
