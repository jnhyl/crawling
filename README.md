# Naver Shopping API Collector

네이버 쇼핑 Open API를 활용한 상품 데이터 수집 및 관리 시스템입니다.
FastAPI + MongoDB 기반으로 구축되었으며, 자연어 기반 검색을 지원합니다.

## 주요 기능

- 네이버 쇼핑 API를 통한 상품 데이터 수집
- MongoDB를 활용한 데이터 저장 및 관리
- FastAPI 기반 RESTful API 제공
- 상세한 상품 정보 및 메타데이터 수집
- 자연어 기반 검색 지원
- 카테고리, 가격, 쇼핑몰별 필터링
- 통계 및 분석 기능

## 시스템 요구사항

- Python 3.8+
- MongoDB 4.4+
- Naver Open API 키 (Client ID, Client Secret)

## 설치 방법

### 1. 저장소 클론 및 이동

```bash
cd crawlingTest
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
```

### 3. 의존성 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 필요한 정보를 입력합니다.

```bash
cp .env.example .env
```

`.env` 파일 내용:

```env
# Naver API Credentials (필수)
NAVER_CLIENT_ID=your_client_id_here
NAVER_CLIENT_SECRET=your_client_secret_here

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=naver_shopping

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# Search Configuration
DEFAULT_DISPLAY=100
MAX_DISPLAY=100
```

### 5. MongoDB 설치 및 실행

Ubuntu/Debian:
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

macOS:
```bash
brew install mongodb-community
brew services start mongodb-community
```

Docker:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## 네이버 API 키 발급 방법

1. [네이버 개발자 센터](https://developers.naver.com/main/) 접속
2. 로그인 후 '애플리케이션 등록' 선택
3. 애플리케이션 이름 입력
4. 사용 API에서 '검색' 선택
5. 비로그인 오픈 API 서비스 환경에서 'WEB 설정' 추가
6. 등록 후 발급된 Client ID와 Client Secret을 `.env` 파일에 입력

## 실행 방법

### 개발 모드로 실행

```bash
python main.py
```

또는

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 프로덕션 모드로 실행

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 문서

서버 실행 후 다음 주소에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 엔드포인트

### 상품 수집

#### POST /products/collect
네이버 쇼핑 API로 상품 검색 후 MongoDB에 저장

**Request:**
```bash
curl -X POST "http://localhost:8000/products/collect?query=갤럭시버즈&max_results=100&sort=sim"
```

**Parameters:**
- `query` (required): 검색 키워드
- `max_results` (optional, default=100): 수집할 최대 상품 수 (1~1000)
- `sort` (optional, default=sim): 정렬 옵션
  - `sim`: 정확도순
  - `date`: 날짜순
  - `asc`: 가격 오름차순
  - `dsc`: 가격 내림차순

**Response:**
```json
{
  "status": "success",
  "query": "갤럭시버즈",
  "total_collected": 100,
  "new_products": 95,
  "updated_products": 5,
  "timestamp": "2025-10-31T04:00:00.000000"
}
```

### 상품 검색

#### GET /products/search
저장된 상품을 다양한 조건으로 검색

**Request:**
```bash
curl -X GET "http://localhost:8000/products/search?keyword=삼성&min_price=100000&max_price=500000&limit=20"
```

**Parameters:**
- `keyword` (optional): 제목, 브랜드, 제조사에서 검색
- `category1` (optional): 카테고리 1단계 필터
- `mall_name` (optional): 쇼핑몰 이름 필터
- `min_price` (optional): 최소 가격
- `max_price` (optional): 최대 가격
- `limit` (optional, default=50): 조회할 최대 결과 수 (1~500)
- `skip` (optional, default=0): 건너뛸 결과 수 (페이지네이션)

### 상품 상세 조회

#### GET /products/{product_id}
특정 상품의 상세 정보 조회

**Request:**
```bash
curl -X GET "http://localhost:8000/products/12345678"
```

### 상품 목록 조회

#### GET /products/
저장된 모든 상품 조회 (페이지네이션)

**Request:**
```bash
curl -X GET "http://localhost:8000/products/?limit=50&skip=0"
```

### 통계 정보

#### GET /products/stats/summary
전체 상품 통계 정보 조회

**Request:**
```bash
curl -X GET "http://localhost:8000/products/stats/summary"
```

**Response:**
```json
{
  "total_products": 1500,
  "top_malls": [
    {"_id": "네이버", "count": 500},
    {"_id": "쿠팡", "count": 300}
  ],
  "top_categories": [
    {"_id": "디지털/가전", "count": 800},
    {"_id": "패션의류", "count": 400}
  ],
  "timestamp": "2025-10-31T04:00:00.000000"
}
```

### 상품 삭제

#### DELETE /products/{product_id}
특정 상품 삭제

**Request:**
```bash
curl -X DELETE "http://localhost:8000/products/12345678"
```

## 프로젝트 구조

```
crawlingTest/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py       # 환경 설정
│   │   └── database.py        # MongoDB 연결 관리
│   ├── models/
│   │   ├── __init__.py
│   │   └── product.py         # 상품 데이터 모델
│   ├── services/
│   │   ├── __init__.py
│   │   └── naver_api.py       # 네이버 API 클라이언트
│   └── routes/
│       ├── __init__.py
│       └── products.py        # 상품 관련 엔드포인트
├── main.py                    # FastAPI 애플리케이션 진입점
├── requirements.txt           # 의존성 패키지
├── .env.example              # 환경 변수 예시
└── README.md                 # 프로젝트 문서
```

## 데이터 모델

### Product (상품)

```python
{
  "product_id": "12345678",           # 상품 고유 ID
  "title": "삼성전자 갤럭시 버즈2",   # 상품명
  "link": "https://...",              # 상품 URL
  "image": "https://...",             # 이미지 URL
  "lprice": 189000,                   # 최저가
  "hprice": 229000,                   # 최고가
  "mallName": "네이버",               # 쇼핑몰
  "maker": "삼성전자",                # 제조사
  "brand": "삼성",                    # 브랜드
  "category1": "디지털/가전",         # 카테고리 1단계
  "category2": "음향가전",            # 카테고리 2단계
  "category3": "이어폰/헤드폰",       # 카테고리 3단계
  "category4": "블루투스이어폰",      # 카테고리 4단계
  "search_keyword": "갤럭시버즈",     # 검색 키워드
  "tags": ["무선", "블루투스"],       # 자동 추출 태그
  "rank": 1,                          # 검색 결과 순위
  "created_at": "2025-10-31T...",     # 수집 시각
  "updated_at": "2025-10-31T..."      # 갱신 시각
}
```

## 사용 예시

### 1. 상품 데이터 수집

```bash
# "무선 이어폰" 키워드로 100개 상품 수집 (정확도순)
curl -X POST "http://localhost:8000/products/collect?query=무선이어폰&max_results=100&sort=sim"

# "노트북" 키워드로 200개 상품 수집 (가격 낮은순)
curl -X POST "http://localhost:8000/products/collect?query=노트북&max_results=200&sort=asc"
```

### 2. 자연어 검색

```bash
# "삼성" 키워드로 검색
curl -X GET "http://localhost:8000/products/search?keyword=삼성"

# 가격 범위로 필터링 (10만원~50만원)
curl -X GET "http://localhost:8000/products/search?keyword=이어폰&min_price=100000&max_price=500000"

# 특정 쇼핑몰의 상품만 검색
curl -X GET "http://localhost:8000/products/search?mall_name=쿠팡"

# 카테고리 필터링
curl -X GET "http://localhost:8000/products/search?category1=디지털/가전"
```

### 3. 페이지네이션

```bash
# 첫 번째 페이지 (0~49)
curl -X GET "http://localhost:8000/products/?limit=50&skip=0"

# 두 번째 페이지 (50~99)
curl -X GET "http://localhost:8000/products/?limit=50&skip=50"
```

## 주요 기술 스택

- **FastAPI**: 고성능 웹 프레임워크
- **MongoDB**: NoSQL 데이터베이스
- **Beanie**: MongoDB용 비동기 ODM
- **Motor**: 비동기 MongoDB 드라이버
- **httpx**: 비동기 HTTP 클라이언트
- **Pydantic**: 데이터 검증 및 설정 관리
- **Tenacity**: 재시도 로직

## 특징

### 1. 상세한 상품 정보 수집
- 네이버 쇼핑 API에서 제공하는 모든 필드 수집
- 카테고리 정보 (최대 4단계)
- 가격 정보 (최저가, 최고가)
- 판매자 정보 (쇼핑몰, 브랜드, 제조사)

### 2. 자연어 검색 지원
- 제목, 브랜드, 제조사에서 키워드 검색
- 자동 태그 추출 및 태그 기반 검색
- MongoDB 텍스트 인덱스 활용

### 3. 고급 필터링
- 가격 범위 필터
- 카테고리 필터
- 쇼핑몰 필터
- 조합 검색 지원

### 4. 중복 방지
- product_id 기반 중복 체크
- 기존 상품은 가격 정보만 업데이트

### 5. 에러 처리
- Tenacity를 활용한 자동 재시도
- 상세한 에러 로깅
- HTTP 상태 코드 기반 예외 처리

## 트러블슈팅

### MongoDB 연결 오류
```
pymongo.errors.ServerSelectionTimeoutError
```
**해결방법**: MongoDB가 실행 중인지 확인
```bash
sudo systemctl status mongodb
```

### 네이버 API 오류
```
HTTP 401 Unauthorized
```
**해결방법**: `.env` 파일의 Client ID와 Secret 확인

### 검색 결과 없음
```
404: 검색 결과가 없습니다
```
**해결방법**: 다른 키워드로 시도하거나 네이버 쇼핑에서 해당 키워드의 상품이 존재하는지 확인

## 라이선스

MIT License

## 기여

이슈 및 PR은 언제나 환영합니다!

## 참고 자료

- [네이버 개발자 센터](https://developers.naver.com/)
- [네이버 검색 API 가이드](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [MongoDB 공식 문서](https://www.mongodb.com/docs/)
- [Beanie ODM 문서](https://beanie-odm.dev/)
