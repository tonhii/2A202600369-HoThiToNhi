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
    # Xử lý triệt để khoảng trắng và ký tự xuống dòng từ Windows/Unix
    expected_key = settings.AGENT_API_KEY.strip().replace('\r', '').replace('\n', '')
    provided_key = api_key.strip().replace('\r', '').replace('\n', '') if api_key else ""

    if not provided_key or provided_key != expected_key:
        # Log mã Hex để tìm ký tự ẩn nếu vẫn không khớp
        expected_hex = expected_key.encode().hex()[:4]
        provided_hex = provided_key.encode().hex()[:4]
        print(f"DEBUG: Auth failed. Expected(hex_prefix): {expected_hex}, Got(hex_prefix): {provided_hex}")
        raise HTTPException(
            status_code=401,
            detail="Tín hiệu không hợp lệ! Vui lòng cung cấp 'X-API-Key' chính xác trong Header."
        )
    
    # Giả lập trả về user_id từ API Key (trong thực tế có thể query database)
    return "user_premium_01"
