import time
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# Import các linh kiện chúng ta đã tạo
from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit
from .cost_guard import check_budget, record_cost
from utils.mock_llm import ask as llm_ask

# Setup Logging JSON
logging.basicConfig(level=logging.INFO, format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}')
logger = logging.getLogger(__name__)

_is_ready = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info(json.dumps({"event": "startup", "msg": "Agent starting up..."}))
    _is_ready = True
    yield
    _is_ready = False
    logger.info(json.dumps({"event": "shutdown", "msg": "Graceful shutdown complete."}))

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "uptime_seconds": "..."}

@app.get("/ready")
def ready():
    if not _is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    return {"status": "ready"}

# ENDPOINT QUAN TRỌNG NHẤT
@app.post("/ask")
async def ask(
    question: str, 
    user_id: str = Depends(verify_api_key) # Bước 4: Kiểm tra Auth
):
    # Bước 5: Kiểm tra Rate Limit
    check_rate_limit(user_id)
    
    # Bước 6: Kiểm tra Budget
    check_budget(user_id)
    
    # Gọi LLM
    answer = llm_ask(question)
    
    # Ghi lại chi phí (Giả sử câu trả lời tốn 500 tokens)
    record_cost(user_id, 500)
    
    return {
        "question": question,
        "answer": answer,
        "user_id": user_id,
        "served_by": "production-agent-final"
    }
