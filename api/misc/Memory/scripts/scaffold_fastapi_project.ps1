# Создание FastAPI+Postgres+Docker проекта с нуля
param(
    [string]$ProjectName = "",
    [string]$ProjectPath = ""
)

# Установка кодировки UTF-8
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()

Write-Host "🚀 Создание FastAPI+Postgres+Docker проекта" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

# Получение имени проекта
if (-not $ProjectName) {
    $ProjectName = Read-Host "Введите имя проекта (например: my-api)"
}

if (-not $ProjectPath) {
    $ProjectPath = "D:\Projects\$ProjectName"
}

Write-Host "`n📋 Параметры проекта:" -ForegroundColor Yellow
Write-Host "Имя: $ProjectName" -ForegroundColor White
Write-Host "Путь: $ProjectPath" -ForegroundColor White

# Создание директории проекта
Write-Host "`n📁 Создание структуры проекта..." -ForegroundColor Yellow
try {
    New-Item -ItemType Directory -Path $ProjectPath -Force | Out-Null
    Set-Location $ProjectPath
    
    # Создание поддиректорий
    $directories = @("app", "app/api", "app/core", "app/models", "app/schemas", "tests", "scripts")
    foreach ($dir in $directories) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Создана директория: $dir" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Ошибка создания директорий: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Создание основных файлов
Write-Host "`n📝 Создание файлов проекта..." -ForegroundColor Yellow

# 1. main.py
$mainPy = @"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI приложение с PostgreSQL и Docker"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Привет от FastAPI!", "project": settings.PROJECT_NAME}

@app.get("/health")
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
"@

Set-Content -Path "main.py" -Value $mainPy -Encoding UTF8
Write-Host "✅ Создан main.py" -ForegroundColor Green

# 2. requirements.txt
$requirements = @"
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
"@

Set-Content -Path "requirements.txt" -Value $requirements -Encoding UTF8
Write-Host "✅ Создан requirements.txt" -ForegroundColor Green

# 3. Dockerfile
$dockerfile = @"
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"@

Set-Content -Path "Dockerfile" -Value $dockerfile -Encoding UTF8
Write-Host "✅ Создан Dockerfile" -ForegroundColor Green

# 4. docker-compose.yml
$dockerCompose = @"
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${ProjectName}_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/${ProjectName}_db
    depends_on:
      - db
    volumes:
      - .:/app

volumes:
  postgres_data:
"@

Set-Content -Path "docker-compose.yml" -Value $dockerCompose -Encoding UTF8
Write-Host "✅ Создан docker-compose.yml" -ForegroundColor Green

# 5. app/core/config.py
$configPy = @"
from pydantic_settings import BaseSettings
from typing import List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "$ProjectName"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/${ProjectName}_db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"

settings = Settings()
"@

Set-Content -Path "app/core/config.py" -Value $configPy -Encoding UTF8
Write-Host "✅ Создан app/core/config.py" -ForegroundColor Green

# 6. app/api/__init__.py
$apiInit = @"
from fastapi import APIRouter
from app.api.endpoints import items, users

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
"@

Set-Content -Path "app/api/__init__.py" -Value $apiInit -Encoding UTF8
Write-Host "✅ Создан app/api/__init__.py" -ForegroundColor Green

# 7. app/api/endpoints/items.py
$itemsPy = @"
from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.item import Item, ItemCreate
from app.models.item import items_db

router = APIRouter()

@router.get("/", response_model=List[Item])
async def read_items():
    return items_db

@router.post("/", response_model=Item)
async def create_item(item: ItemCreate):
    new_item = Item(
        id=len(items_db) + 1,
        name=item.name,
        description=item.description,
        price=item.price
    )
    items_db.append(new_item)
    return new_item

@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")
"@

New-Item -ItemType Directory -Path "app/api/endpoints" -Force | Out-Null
Set-Content -Path "app/api/endpoints/items.py" -Value $itemsPy -Encoding UTF8
Write-Host "✅ Создан app/api/endpoints/items.py" -ForegroundColor Green

# 8. app/api/endpoints/users.py
$usersPy = @"
from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.user import User, UserCreate
from app.models.user import users_db

router = APIRouter()

@router.get("/", response_model=List[User])
async def read_users():
    return users_db

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    new_user = User(
        id=len(users_db) + 1,
        email=user.email,
        name=user.name
    )
    users_db.append(new_user)
    return new_user

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")
"@

Set-Content -Path "app/api/endpoints/users.py" -Value $usersPy -Encoding UTF8
Write-Host "✅ Создан app/api/endpoints/users.py" -ForegroundColor Green

# 9. app/schemas/item.py
$itemSchema = @"
from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    
    class Config:
        from_attributes = True
"@

Set-Content -Path "app/schemas/item.py" -Value $itemSchema -Encoding UTF8
Write-Host "✅ Создан app/schemas/item.py" -ForegroundColor Green

# 10. app/schemas/user.py
$userSchema = @"
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True
"@

Set-Content -Path "app/schemas/user.py" -Value $userSchema -Encoding UTF8
Write-Host "✅ Создан app/schemas/user.py" -ForegroundColor Green

# 11. app/models/item.py
$itemModel = @"
from typing import List
from app.schemas.item import Item

# Временная база данных в памяти
items_db: List[Item] = [
    Item(id=1, name="Тестовый товар", description="Описание товара", price=99.99)
]
"@

Set-Content -Path "app/models/item.py" -Value $itemModel -Encoding UTF8
Write-Host "✅ Создан app/models/item.py" -ForegroundColor Green

# 12. app/models/user.py
$userModel = @"
from typing import List
from app.schemas.user import User

# Временная база данных в памяти
users_db: List[User] = [
    User(id=1, email="admin@example.com", name="Администратор")
]
"@

Set-Content -Path "app/models/user.py" -Value $userModel -Encoding UTF8
Write-Host "✅ Создан app/models/user.py" -ForegroundColor Green

# 13. .env файл
$envFile = @"
PROJECT_NAME=$ProjectName
VERSION=1.0.0
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/${ProjectName}_db
"@

Set-Content -Path ".env" -Value $envFile -Encoding UTF8
Write-Host "✅ Создан .env" -ForegroundColor Green

# 14. ProjectSpec.yml для AI-Agent
$projectSpec = @"
name: $ProjectName
description: FastAPI приложение с PostgreSQL и Docker
version: "1.0.0"

stages:
  setup:
    description: "Настройка проекта"
    steps:
      - name: "Установка зависимостей"
        command: "pip install -r requirements.txt"
        type: "install"
      
      - name: "Проверка структуры"
        command: "python -c 'import app.core.config; print(\"Config loaded\")'"
        type: "test"

  run:
    description: "Запуск приложения"
    steps:
      - name: "Запуск базы данных"
        command: "docker-compose up -d db"
        type: "docker"
        wait_for: "database"
      
      - name: "Запуск API"
        command: "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
        type: "server"
        port: 8000

  test:
    description: "Тестирование"
    steps:
      - name: "Проверка здоровья"
        command: "curl http://localhost:8000/health"
        type: "http"
        expected_status: 200
      
      - name: "Тест API"
        command: "curl http://localhost:8000/api/v1/items/"
        type: "http"
        expected_status: 200

environment:
  python: "3.11"
  database: "postgresql"
  framework: "fastapi"
"@

Set-Content -Path "ProjectSpec.yml" -Value $projectSpec -Encoding UTF8
Write-Host "✅ Создан ProjectSpec.yml" -ForegroundColor Green

# 15. README.md
$readme = @"
# $ProjectName

FastAPI приложение с PostgreSQL и Docker.

## Быстрый старт

### 1. Запуск через Docker Compose
```bash
docker-compose up -d
```

### 2. Запуск локально
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск базы данных
docker-compose up -d db

# Запуск API
uvicorn main:app --reload
```

## API Endpoints

- `GET /` - Главная страница
- `GET /health` - Проверка здоровья
- `GET /api/v1/items/` - Список товаров
- `POST /api/v1/items/` - Создать товар
- `GET /api/v1/users/` - Список пользователей
- `POST /api/v1/users/` - Создать пользователя

## Документация API

После запуска доступна по адресу: http://localhost:8000/docs

## Структура проекта

```
$ProjectName/
├── app/
│   ├── api/
│   │   └── endpoints/
│   ├── core/
│   ├── models/
│   └── schemas/
├── tests/
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── ProjectSpec.yml
```
"@

Set-Content -Path "README.md" -Value $readme -Encoding UTF8
Write-Host "✅ Создан README.md" -ForegroundColor Green

Write-Host "`n🎉 Проект '$ProjectName' создан успешно!" -ForegroundColor Green
Write-Host "`n📁 Расположение: $ProjectPath" -ForegroundColor Cyan
Write-Host "`n🚀 Следующие шаги:" -ForegroundColor Yellow
Write-Host "1. cd $ProjectPath" -ForegroundColor White
Write-Host "2. docker-compose up -d" -ForegroundColor White
Write-Host "3. Откройте http://localhost:8000/docs" -ForegroundColor White
Write-Host "`n💡 Для управления через AI-Agent используйте ProjectSpec.yml" -ForegroundColor Cyan

