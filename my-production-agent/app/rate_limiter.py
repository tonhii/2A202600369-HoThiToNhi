import time
import redis
from fastapi import HTTPException
from .config import settings

# 1. Kết nối tới Redis chung
try:
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    # Fallback nếu không có Redis (chỉ dùng cho local test)
    r = None

def check_rate_limit(user_id: str):
    """
    Sử dụng kỹ thuật Fixed Window với Redis.
    Mỗi user được phép gọi tối đa 'rate_limit_per_minute' lần mỗi phút.
    """
    if r is None:
        return # Bỏ qua nếu không có Redis

    # Tạo key theo từng phút: ví dụ rate_limit:user_01:2026-04-17-23-14
    current_minute = time.strftime("%Y-%m-%d-%H-%M")
    key = f"rate_limit:{user_id}:{current_minute}"

    try:
        # Tăng giá trị key lên 1
        count = r.incr(key)
        
        # Nếu là lần đầu gọi trong phút này, đặt thời gian hết hạn sau 60s
        if count == 1:
            r.expire(key, 60)
            
        # Nếu vượt quá giới hạn -> Chặn
        if count > settings.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=429,
                detail=f"Bạn đã gọi quá nhanh! Giới hạn: {settings.RATE_LIMIT_PER_MINUTE} req/phút."
            )
    except redis.RedisError:
        # Nếu Redis lỗi, cho phép qua (fail-safe) để không làm chết app
        pass
