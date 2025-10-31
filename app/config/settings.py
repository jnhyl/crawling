from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    애플리케이션 설정
    환경변수 또는 .env 파일에서 로드
    """

    # Naver API
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "naver_shopping"

    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # Search Configuration
    DEFAULT_DISPLAY: int = 100
    MAX_DISPLAY: int = 100

    # Naver Shopping API URL
    NAVER_SHOPPING_API_URL: str = "https://openapi.naver.com/v1/search/shop.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
