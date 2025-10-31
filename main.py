from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from app.config.database import db
from app.routes import products_router
from app.config import settings
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작/종료 시 실행되는 이벤트
    """
    # 시작 시
    logger.info("Starting application...")
    await db.connect_db()
    logger.info("Database connected successfully")

    yield

    # 종료 시
    logger.info("Shutting down application...")
    await db.close_db()
    logger.info("Database connection closed")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="Naver Shopping API Collector",
    description="네이버 쇼핑 API를 활용한 상품 데이터 수집 및 관리 시스템",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 라우터 등록
app.include_router(products_router)


@app.get("/", response_class=HTMLResponse, tags=["web"])
async def index(request: Request):
    """
    웹 UI 메인 페이지
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api", tags=["root"])
async def api_root():
    """
    API 루트 엔드포인트
    """
    return {
        "message": "Naver Shopping API Collector",
        "version": "1.0.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "web_ui": "/"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {
        "status": "healthy",
        "database": "connected" if db.client else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
