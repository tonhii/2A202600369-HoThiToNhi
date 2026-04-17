FROM python:3.12-slim

WORKDIR /app

# Cài đặt các thư viện cần thiết
COPY 05-scaling-reliability/production/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code và utils
COPY 05-scaling-reliability/production/app.py .
COPY utils/ ./utils/

# Môi trường
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Chạy App
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
