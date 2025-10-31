# 설치 및 설정 가이드

## GitHub에 등록되지 않는 파일들

다음 파일들은 `.gitignore`에 의해 GitHub에 업로드되지 않습니다:

### 1. 환경 설정 파일
- `.env` - API 키 및 민감한 정보 (보안상 필수 제외)
- `.env.example` - 템플릿으로 제공됨 (GitHub에 포함)

### 2. 가상환경
- `.venv/` - Python 가상환경 전체 디렉토리

### 3. Python 캐시
- `__pycache__/` - Python 바이트코드 캐시
- `*.pyc`, `*.pyo` - 컴파일된 Python 파일

### 4. IDE 설정
- `.vscode/` - VS Code 설정
- `.idea/` - PyCharm 설정

### 5. 로그 및 데이터베이스
- `*.log` - 로그 파일
- `*.db`, `*.sqlite` - 로컬 데이터베이스 파일

### 6. OS 파일
- `.DS_Store` (macOS)
- `Thumbs.db` (Windows)

---

## 로컬 환경 설정 가이드

### 사전 준비 사항

다음 소프트웨어가 설치되어 있어야 합니다:

1. **Python 3.8 이상**
   ```bash
   python --version  # 또는 python3 --version
   ```

2. **MongoDB 4.4 이상**
   ```bash
   mongod --version
   ```

3. **Git**
   ```bash
   git --version
   ```

---

## 설치 단계별 가이드

### 1단계: 저장소 클론

```bash
git clone https://github.com/your-username/crawlingTest.git
cd crawlingTest
```

### 2단계: Python 가상환경 생성

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
# Linux/macOS:
source .venv/bin/activate

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (CMD):
.venv\Scripts\activate.bat
```

가상환경이 활성화되면 터미널 프롬프트 앞에 `(.venv)`가 표시됩니다.

### 3단계: 의존성 패키지 설치

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**설치되는 주요 패키지:**
- `fastapi` - 웹 프레임워크
- `uvicorn` - ASGI 서버
- `motor` - MongoDB 비동기 드라이버
- `beanie` - MongoDB ODM
- `httpx` - HTTP 클라이언트
- `python-dotenv` - 환경 변수 관리
- `tenacity` - 재시도 로직
- `pydantic` - 데이터 검증
- `jinja2` - 템플릿 엔진

### 4단계: 환경 변수 설정

1. `.env.example` 파일을 복사하여 `.env` 파일 생성:

```bash
cp .env.example .env
```

2. `.env` 파일을 편집기로 열어 다음 정보 입력:

```env
# Naver API Credentials (필수)
NAVER_CLIENT_ID=your_actual_client_id_here
NAVER_CLIENT_SECRET=your_actual_client_secret_here

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

**중요:** `NAVER_CLIENT_ID`와 `NAVER_CLIENT_SECRET`에 실제 네이버 API 키를 입력해야 합니다.

### 5단계: 네이버 API 키 발급

1. [네이버 개발자 센터](https://developers.naver.com/main/) 접속
2. 로그인 후 **'애플리케이션 등록'** 클릭
3. 다음 정보 입력:
   - **애플리케이션 이름**: 원하는 이름 (예: "상품 데이터 수집")
   - **사용 API**: **검색** 선택
   - **비로그인 오픈API 서비스 환경**: **WEB 설정** 추가
     - 웹 서비스 URL: `http://localhost:8000` (개발용)
4. 등록 완료 후 **Client ID**와 **Client Secret** 복사
5. `.env` 파일에 붙여넣기

### 6단계: MongoDB 설치 및 실행

#### Ubuntu/Debian:
```bash
# MongoDB 설치
sudo apt-get update
sudo apt-get install -y mongodb

# MongoDB 실행
sudo systemctl start mongodb

# 상태 확인
sudo systemctl status mongodb

# 자동 시작 설정
sudo systemctl enable mongodb
```

#### macOS (Homebrew):
```bash
# MongoDB Community Edition 설치
brew tap mongodb/brew
brew install mongodb-community

# MongoDB 실행
brew services start mongodb-community

# 상태 확인
brew services list
```

#### Windows:
1. [MongoDB 공식 사이트](https://www.mongodb.com/try/download/community)에서 설치 프로그램 다운로드
2. 설치 후 서비스로 자동 실행되거나 수동 실행:
   ```cmd
   "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath="C:\data\db"
   ```

#### Docker 사용 (선택사항):
```bash
# MongoDB 컨테이너 실행
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:latest

# 상태 확인
docker ps | grep mongodb
```

### 7단계: MongoDB 연결 테스트

```bash
# MongoDB 쉘 접속
mongosh

# 데이터베이스 목록 확인
show dbs

# 종료
exit
```

### 8단계: 서버 실행

```bash
# 개발 모드 (자동 재로드)
python main.py
```

또는

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**서버 실행 성공 메시지:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
2025-10-31 XX:XX:XX - main - INFO - Starting application...
2025-10-31 XX:XX:XX - app.config.database - INFO - Connected to MongoDB: naver_shopping
2025-10-31 XX:XX:XX - main - INFO - Database connected successfully
INFO:     Application startup complete.
```

### 9단계: 동작 확인

브라우저에서 다음 주소로 접속:

1. **웹 UI**: http://localhost:8000
2. **API 문서 (Swagger)**: http://localhost:8000/docs
3. **API 문서 (ReDoc)**: http://localhost:8000/redoc

또는 터미널에서:

```bash
# 상태 확인
curl http://localhost:8000/products/stats/summary

# 상품 목록 조회
curl http://localhost:8000/products/?limit=5
```

---

## 자주 발생하는 문제 해결

### 1. 가상환경 활성화 안 됨
**증상:** `pip install` 실행 시 전역에 설치되거나 권한 오류

**해결:**
```bash
# 가상환경이 활성화되었는지 확인 (프롬프트에 (.venv) 표시)
which python  # Linux/macOS
where python  # Windows

# 활성화 다시 시도
source .venv/bin/activate  # Linux/macOS
```

### 2. MongoDB 연결 오류
**증상:** `pymongo.errors.ServerSelectionTimeoutError`

**해결:**
```bash
# MongoDB 실행 상태 확인
sudo systemctl status mongodb  # Linux
brew services list  # macOS
netstat -an | grep 27017  # 포트 확인

# MongoDB 재시작
sudo systemctl restart mongodb  # Linux
brew services restart mongodb-community  # macOS
```

### 3. 네이버 API 401 오류
**증상:** `HTTP 401 Unauthorized`

**원인 및 해결:**
- `.env` 파일에 실제 API 키가 입력되지 않음
- 네이버 개발자 센터에서 API 키 확인
- `.env` 파일 내용 확인:
  ```bash
  cat .env
  ```
- 서버 재시작

### 4. 포트 이미 사용 중
**증상:** `Address already in use`

**해결:**
```bash
# 포트 8000 사용 프로세스 확인
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# 프로세스 종료
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows
```

### 5. 모듈을 찾을 수 없음
**증상:** `ModuleNotFoundError: No module named 'xxx'`

**해결:**
```bash
# 가상환경 활성화 확인
source .venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt
```

---

## 개발 환경 설정 (선택사항)

### VS Code 설정

1. Python 확장 설치
2. `.vscode/settings.json` 생성:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

### PyCharm 설정

1. Project Interpreter 설정: `.venv/bin/python` 선택
2. Run Configuration 생성:
   - Script path: `main.py`
   - Working directory: 프로젝트 루트

---

## 프로덕션 배포 시 주의사항

1. **환경 변수**
   - `.env` 파일 대신 서버 환경 변수 사용
   - API 키는 절대 GitHub에 업로드하지 않기

2. **API 설정**
   ```env
   API_RELOAD=False
   ```

3. **MongoDB**
   - 인증 설정
   - 원격 접속 제한
   - 정기 백업

4. **서버 실행**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

5. **방화벽 설정**
   - 필요한 포트만 개방 (8000, 27017)

---

## 도움말

문제가 해결되지 않으면:

1. [GitHub Issues](https://github.com/your-username/crawlingTest/issues) 확인
2. 로그 파일 확인
3. MongoDB 로그 확인: `/var/log/mongodb/mongod.log`
4. [네이버 개발자 센터 FAQ](https://developers.naver.com/docs/common/openapiguide/)

---

## 참고 자료

- [Python 가상환경 공식 문서](https://docs.python.org/ko/3/library/venv.html)
- [MongoDB 설치 가이드](https://www.mongodb.com/docs/manual/installation/)
- [네이버 API 가이드](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
