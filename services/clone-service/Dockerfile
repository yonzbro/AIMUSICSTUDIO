FROM python:3.10-slim

WORKDIR /app

# FFmpeg for audio validation and format conversion
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create persistent voice profiles directory
RUN mkdir -p /app/voice_profiles

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
