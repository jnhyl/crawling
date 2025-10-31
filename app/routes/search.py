from fastapi import APIRouter
from typing import List
from app.models import Product

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/brands")
async def get_brands() -> List[str]:
    """
    모든 브랜드 목록 반환
    """
    pipeline = [
        {"$match": {"brand": {"$ne": None, "$ne": ""}}},
        {"$group": {"_id": "$brand"}},
        {"$sort": {"_id": 1}},
        {"$limit": 100}
    ]

    results = await Product.aggregate(pipeline).to_list()
    return [r["_id"] for r in results if r["_id"]]


@router.get("/categories")
async def get_categories() -> List[str]:
    """
    모든 카테고리1 목록 반환
    """
    pipeline = [
        {"$match": {"category1": {"$ne": None, "$ne": ""}}},
        {"$group": {"_id": "$category1"}},
        {"$sort": {"_id": 1}}
    ]

    results = await Product.aggregate(pipeline).to_list()
    return [r["_id"] for r in results if r["_id"]]


@router.get("/malls")
async def get_malls() -> List[str]:
    """
    모든 쇼핑몰 목록 반환
    """
    pipeline = [
        {"$match": {"mallName": {"$ne": None, "$ne": ""}}},
        {"$group": {"_id": "$mallName"}},
        {"$sort": {"_id": 1}},
        {"$limit": 100}
    ]

    results = await Product.aggregate(pipeline).to_list()
    return [r["_id"] for r in results if r["_id"]]


@router.get("/tags")
async def get_tags() -> List[str]:
    """
    자주 사용되는 태그 목록 반환 (상위 100개)
    """
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 100}
    ]

    results = await Product.aggregate(pipeline).to_list()
    return [r["_id"] for r in results if r["_id"]]
