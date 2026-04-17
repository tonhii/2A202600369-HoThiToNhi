import time
import logging
import os
from dataclasses import dataclass, field
from fastapi import HTTPException
import redis

logger = logging.getLogger(__name__)

# Giá token (tham khảo, thay đổi theo model)
PRICE_PER_1K_INPUT_TOKENS = 0.00015   # GPT-4o-mini: $0.15/1M input
PRICE_PER_1K_OUTPUT_TOKENS = 0.0006   # GPT-4o-mini: $0.60/1M output

@dataclass
class UsageRecord:
    user_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    request_count: int = 0
    day: str = field(default_factory=lambda: time.strftime("%Y-%m-%d"))

    @property
    def total_cost_usd(self) -> float:
        input_cost = (self.input_tokens / 1000) * PRICE_PER_1K_INPUT_TOKENS
        output_cost = (self.output_tokens / 1000) * PRICE_PER_1K_OUTPUT_TOKENS
        return round(input_cost + output_cost, 6)

class CostGuard:
    def __init__(
        self,
        daily_budget_usd: float = 1.0,       # $1/ngày per user
        global_daily_budget_usd: float = 10.0, # $10/ngày tổng cộng
        warn_at_pct: float = 0.8,              # Cảnh báo khi dùng 80%
    ):
        self.daily_budget_usd = daily_budget_usd
        self.global_daily_budget_usd = global_daily_budget_usd
        self.warn_at_pct = warn_at_pct
        
        # Connect to Redis
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            decode_responses=True
        )
        logger.info(f"CostGuard initialized with Redis at {redis_host}:{redis_port}")

    def _get_keys(self, user_id: str):
        today = time.strftime("%Y-%m-%d")
        return f"cost:user:{user_id}:{today}", f"cost:global:{today}"

    def check_budget(self, user_id: str) -> None:
        """Kiểm tra budget trước khi gọi LLM."""
        user_key, global_key = self._get_keys(user_id)
        
        # Global budget check
        global_cost = float(self.redis.get(global_key) or 0)
        if global_cost >= self.global_daily_budget_usd:
            logger.critical(f"GLOBAL BUDGET EXCEEDED: ${global_cost:.4f}")
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable due to budget limits. Try again tomorrow.",
            )

        # Per-user budget check
        data = self.redis.hgetall(user_key)
        input_tokens = int(data.get("input", 0))
        output_tokens = int(data.get("output", 0))
        
        current_cost = (input_tokens / 1000 * PRICE_PER_1K_INPUT_TOKENS +
                        output_tokens / 1000 * PRICE_PER_1K_OUTPUT_TOKENS)

        if current_cost >= self.daily_budget_usd:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Daily budget exceeded",
                    "used_usd": round(current_cost, 6),
                    "budget_usd": self.daily_budget_usd,
                    "resets_at": "midnight UTC",
                },
            )

        if current_cost >= self.daily_budget_usd * self.warn_at_pct:
            logger.warning(f"User {user_id} at {current_cost/self.daily_budget_usd*100:.0f}% budget")

    def record_usage(self, user_id: str, input_tokens: int, output_tokens: int) -> UsageRecord:
        """Ghi nhận usage sau khi gọi LLM xong."""
        user_key, global_key = self._get_keys(user_id)
        
        # Update User Stats
        self.redis.hincrby(user_key, "input", input_tokens)
        self.redis.hincrby(user_key, "output", output_tokens)
        self.redis.hincrby(user_key, "count", 1)
        self.redis.expire(user_key, 2 * 24 * 3600)  # Keep for 2 days

        # Update Global Cost
        cost = (input_tokens / 1000 * PRICE_PER_1K_INPUT_TOKENS +
                output_tokens / 1000 * PRICE_PER_1K_OUTPUT_TOKENS)
        self.redis.incrbyfloat(global_key, cost)
        self.redis.expire(global_key, 2 * 24 * 3600)

        # Return a DTO for the response
        data = self.redis.hgetall(user_key)
        return UsageRecord(
            user_id=user_id,
            input_tokens=int(data.get("input", 0)),
            output_tokens=int(data.get("output", 0)),
            request_count=int(data.get("count", 0)),
        )

    def get_usage(self, user_id: str) -> dict:
        user_key, _ = self._get_keys(user_id)
        data = self.redis.hgetall(user_key)
        
        input_t = int(data.get("input", 0))
        output_t = int(data.get("output", 0))
        cost_usd = round((input_t / 1000 * PRICE_PER_1K_INPUT_TOKENS +
                         output_t / 1000 * PRICE_PER_1K_OUTPUT_TOKENS), 6)

        return {
            "user_id": user_id,
            "date": time.strftime("%Y-%m-%d"),
            "requests": int(data.get("count", 0)),
            "input_tokens": input_t,
            "output_tokens": output_t,
            "cost_usd": cost_usd,
            "budget_usd": self.daily_budget_usd,
            "budget_remaining_usd": max(0, round(self.daily_budget_usd - cost_usd, 6)),
            "budget_used_pct": round(cost_usd / self.daily_budget_usd * 100, 1),
        }

# Singleton
cost_guard = CostGuard(daily_budget_usd=1.0, global_daily_budget_usd=10.0)
