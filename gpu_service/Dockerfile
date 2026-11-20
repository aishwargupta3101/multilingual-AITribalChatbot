FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

ENV PYTHONUNBUFFERED=1 \
    TOKENIZERS_PARALLELISM=false \
    HF_HOME=/runpod-volume/huggingface \
    TRANSFORMERS_CACHE=/runpod-volume/huggingface

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-runpod.txt /app/requirements-runpod.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r /app/requirements-runpod.txt
COPY runpod_handler.py /app/runpod_handler.py
CMD ["python", "-u", "/app/runpod_handler.py"]
