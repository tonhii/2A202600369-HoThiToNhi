from fastapi import Header, HTTPException, Security
from fastapi.security import APIKeyHeader
from .config import settings

# 1. Định nghĩa header X-API-Key là bắt buộc
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Hàm kiểm tra API Key.
    Nếu sai hoặc thiếu -> Trả về lỗi 401 Unauthorized.
    Nếu đúng -> Trả về ID của user (giả lập).
    """
    if not api_key or api_key != settings.AGENT_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Tín hiệu không hợp lệ! Vui lòng cung cấp 'X-API-Key' chính xác trong Header."
        )
    
    # Giả lập trả về user_id từ API Key (trong thực tế có thể query database)
    return "user_premium_01"
