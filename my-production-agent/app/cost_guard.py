import redis
from fastapi import HTTPException
from .config import settings
import time

# Kết nối Redis
try:
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    r = None

def check_budget(user_id: str):
    """
    Kiểm tra xem User này đã tiêu hết ngân sách ngày chưa.
    Giới hạn được lấy từ settings.DAILY_BUDGET_USD
    """
    if r is None:
        return

    today = time.strftime("%Y-%m-%d")
    key = f"cost:{user_id}:{today}"

    current_cost = float(r.get(key) or 0.0)

    if current_cost >= settings.DAILY_BUDGET_USD:
        raise HTTPException(
            status_code=402, 
            detail=f"Thanh toán thất bại: Bạn đã tiêu hết ngân sách {settings.DAILY_BUDGET_USD}$ của ngày hôm nay."
        )

def record_cost(user_id: str, tokens: int):
    """
    Ghi nhận chi phí sau mỗi lần gọi LLM thành công.
    Giả sử 1000 tokens = 0.002$
    """
    if r is None:
        return
        
    cost = (tokens / 1000) * 0.002
    today = time.strftime("%Y-%m-%d")
    key = f"cost:{user_id}:{today}"
    
    # Cộng dồn chi phí vào Redis
    r.incrbyfloat(key, cost)
    r.expire(key, 86400) # Lưu 1 ngày
