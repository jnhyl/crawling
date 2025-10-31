from beanie import Document
from datetime import datetime
from typing import Optional


class ApiUsage(Document):
    """
    네이버 API 사용량 추적
    """
    date: str  # YYYY-MM-DD 형식
    total_calls: int = 0
    last_call_time: Optional[datetime] = None

    # 네이버 API 응답 헤더 정보
    quota_limit: Optional[int] = None  # X-RateLimit-Limit
    quota_remaining: Optional[int] = None  # X-RateLimit-Remaining

    class Settings:
        name = "api_usage"
        indexes = [
            "date",
        ]
