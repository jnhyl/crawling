from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import Product, ProductSearchResponse, ApiUsage
from app.services import naver_api
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/collect", response_model=dict)
async def collect_products(
    query: str = Query(..., description="검색 키워드"),
    max_results: int = Query(100, ge=1, le=1000, description="수집할 최대 결과 수"),
    sort: str = Query("sim", regex="^(sim|date|asc|dsc)$", description="정렬 옵션 (sim: 정확도, date: 날짜, asc: 가격↑, dsc: 가격↓)"),
    filter: Optional[str] = Query(None, regex="^(naverpay)$", description="필터 옵션 (naverpay: 네이버페이 연동 상품만)"),
    exclude: Optional[str] = Query(None, description="제외 옵션 (used:중고, rental:렌탈, cbshop:해외직구/구매대행, 콜론으로 구분)")
):
    """
    네이버 쇼핑 API로 상품 검색 후 MongoDB에 저장

    - **query**: 검색 키워드
    - **max_results**: 수집할 최대 상품 수 (1~1000)
    - **sort**: 정렬 옵션
    - **filter**: 네이버페이 연동 상품만 검색 (naverpay)
    - **exclude**: 제외할 상품 유형 (used:중고, rental:렌탈, cbshop:해외직구)
    """
    try:
        # 필터 옵션 구성
        filter_options = {}
        if filter:
            filter_options["filter"] = filter
        if exclude:
            filter_options["exclude"] = exclude

        # 네이버 API로 상품 검색 및 수집
        products = await naver_api.search_and_collect(
            query=query,
            max_results=max_results,
            sort=sort,
            filter_options=filter_options if filter_options else None
        )

        if not products:
            raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")

        # MongoDB에 저장
        saved_count = 0
        updated_count = 0

        for product in products:
            # 기존 상품 확인 (product_id 기준)
            existing = await Product.find_one(Product.product_id == product.product_id)

            if existing:
                # 업데이트
                existing.lprice = product.lprice
                existing.hprice = product.hprice
                existing.updated_at = datetime.utcnow()
                await existing.save()
                updated_count += 1
            else:
                # 신규 저장
                await product.insert()
                saved_count += 1

        # 검색 이력 저장
        search_history = ProductSearchResponse(
            search_keyword=query,
            total_count=len(products),
            display=max_results,
            start=1,
            collected_at=datetime.utcnow()
        )
        await search_history.insert()

        return {
            "status": "success",
            "query": query,
            "total_collected": len(products),
            "new_products": saved_count,
            "updated_products": updated_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error collecting products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상품 수집 중 오류가 발생했습니다: {str(e)}")


@router.get("/search", response_model=List[Product])
async def search_products(
    keyword: Optional[str] = Query(None, description="검색 키워드 (제목, 브랜드, 제조사)"),
    category1: Optional[str] = Query(None, description="카테고리 1단계"),
    mall_name: Optional[str] = Query(None, description="쇼핑몰 이름"),
    min_price: Optional[int] = Query(None, ge=0, description="최소 가격"),
    max_price: Optional[int] = Query(None, ge=0, description="최대 가격"),
    limit: int = Query(50, ge=1, le=500, description="조회할 최대 결과 수"),
    skip: int = Query(0, ge=0, description="건너뛸 결과 수 (페이지네이션)")
):
    """
    MongoDB에 저장된 상품 검색

    - **keyword**: 제목, 브랜드, 제조사에서 검색
    - **category1**: 카테고리 필터
    - **mall_name**: 쇼핑몰 필터
    - **min_price**: 최소 가격
    - **max_price**: 최대 가격
    - **limit**: 조회할 최대 결과 수
    - **skip**: 건너뛸 결과 수 (페이지네이션용)
    """
    try:
        # 쿼리 빌더
        query_conditions = []

        if keyword:
            # 텍스트 검색 (제목, 브랜드, 제조사)
            query_conditions.append({
                "$or": [
                    {"title": {"$regex": keyword, "$options": "i"}},
                    {"brand": {"$regex": keyword, "$options": "i"}},
                    {"maker": {"$regex": keyword, "$options": "i"}},
                    {"tags": {"$in": [keyword]}}
                ]
            })

        if category1:
            query_conditions.append({"category1": category1})

        if mall_name:
            query_conditions.append({"mallName": {"$regex": mall_name, "$options": "i"}})

        if min_price is not None or max_price is not None:
            price_condition = {}
            if min_price is not None:
                price_condition["$gte"] = min_price
            if max_price is not None:
                price_condition["$lte"] = max_price
            query_conditions.append({"lprice": price_condition})

        # 최종 쿼리 구성
        if query_conditions:
            final_query = {"$and": query_conditions}
            products = await Product.find(final_query).skip(skip).limit(limit).to_list()
        else:
            products = await Product.find_all().skip(skip).limit(limit).to_list()

        return products

    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상품 검색 중 오류가 발생했습니다: {str(e)}")


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """
    특정 상품 상세 정보 조회

    - **product_id**: 상품 고유 ID
    """
    product = await Product.find_one(Product.product_id == product_id)

    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    return product


@router.get("/", response_model=List[Product])
async def list_products(
    limit: int = Query(50, ge=1, le=500, description="조회할 최대 결과 수"),
    skip: int = Query(0, ge=0, description="건너뛸 결과 수")
):
    """
    저장된 모든 상품 조회 (페이지네이션)

    - **limit**: 조회할 최대 결과 수
    - **skip**: 건너뛸 결과 수
    """
    try:
        products = await Product.find_all().skip(skip).limit(limit).to_list()
        return products
    except Exception as e:
        logger.error(f"Error listing products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상품 조회 중 오류가 발생했습니다: {str(e)}")


@router.delete("/{product_id}")
async def delete_product(product_id: str):
    """
    특정 상품 삭제

    - **product_id**: 상품 고유 ID
    """
    product = await Product.find_one(Product.product_id == product_id)

    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    await product.delete()

    return {"status": "success", "message": f"상품 {product_id}가 삭제되었습니다."}


@router.get("/stats/summary", response_model=dict)
async def get_stats():
    """
    전체 상품 통계 정보
    """
    try:
        total_products = await Product.count()

        # 쇼핑몰별 집계
        pipeline = [
            {"$group": {"_id": "$mallName", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        mall_stats = await Product.aggregate(pipeline).to_list()

        # 카테고리별 집계
        pipeline = [
            {"$group": {"_id": "$category1", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        category_stats = await Product.aggregate(pipeline).to_list()

        return {
            "total_products": total_products,
            "top_malls": mall_stats,
            "top_categories": category_stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/stats/api-usage", response_model=dict)
async def get_api_usage():
    """
    당일 API 사용량 조회
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        usage = await ApiUsage.find_one(ApiUsage.date == today)

        if not usage:
            return {
                "date": today,
                "total_calls": 0,
                "quota_limit": 25000,  # 네이버 API 기본 일일 한도
                "quota_remaining": 25000,
                "last_call_time": None
            }

        return {
            "date": usage.date,
            "total_calls": usage.total_calls,
            "quota_limit": usage.quota_limit or 25000,
            "quota_remaining": usage.quota_remaining or (25000 - usage.total_calls),
            "last_call_time": usage.last_call_time.isoformat() if usage.last_call_time else None
        }

    except Exception as e:
        logger.error(f"Error getting API usage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"API 사용량 조회 중 오류가 발생했습니다: {str(e)}")
