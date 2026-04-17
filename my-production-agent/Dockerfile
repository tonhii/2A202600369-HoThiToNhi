# --- Stage 1: Builder ---
FROM python:3.12-slim as builder

WORKDIR /build

# Cài đặt công cụ build
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

# Cài đặt thư viện vào một thư mục tạm
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Stage 2: Runtime ---
FROM python:3.12-slim

WORKDIR /app

# Chỉ copy những thư viện đã cài đặt từ builder sang
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy mã nguồn dự án
COPY app/ ./app/
COPY utils/ ./utils/

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Chạy ứng dụng bằng uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
