FROM python:3.11-slim
WORKDIR /app
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ENV STREAMLIT_SERVER_RUN_ON_SAVE=false
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    torch==2.5.1+cpu \
    torchaudio==2.5.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY . .
EXPOSE 8000
EXPOSE 10000
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/fastapi.log 2>&1 & API_PID=$!; sleep 5; cat /tmp/fastapi.log; if ! kill -0 $API_PID 2>/dev/null; then echo '===== FASTAPI FAILED ====='; cat /tmp/fastapi.log; exit 1; fi; exec streamlit run frontend/app.py --server.address 0.0.0.0 --server.port 10000"]