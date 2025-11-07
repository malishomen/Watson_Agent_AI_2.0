#!/usr/bin/env pwsh
# PROJECT_TEMPLATE.ps1 - автосоздание нового проекта для Watson Agent

param(
    [Parameter(Mandatory=$true)]
    [string]$Name,
    
    [string]$Path = "D:\projects\Projects_by_Watson_Local_Agent",
    
    [string]$BaseRoot,  # deprecated, use -Path instead
    
    [ValidateSet('none', 'react-vite')]
    [string]$WithFrontend = 'none'
)

# Backward compatibility
if ($BaseRoot) {
    $Path = $BaseRoot
}

$ErrorActionPreference = 'Stop'

Write-Host "`n[PROJECT] Creating new Watson project: $Name" -ForegroundColor Cyan
if ($WithFrontend -ne 'none') {
    Write-Host "[PROJECT] With frontend: $WithFrontend" -ForegroundColor Cyan
}

# 1. Создаём структуру
$projectPath = Join-Path $Path $Name
if (Test-Path $projectPath) {
    Write-Host "⚠️  Project already exists: $projectPath" -ForegroundColor Yellow
    $confirm = Read-Host "Overwrite? (y/N)"
    if ($confirm -ne 'y') {
        Write-Host "Cancelled." -ForegroundColor Red
        exit 1
    }
    Remove-Item -Recurse -Force $projectPath
}

New-Item -ItemType Directory -Path $projectPath -Force | Out-Null
Push-Location $projectPath

try {
    # 2. Инициализация git
    git init
    
    # 3. Создаём .gitignore
    @"
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
*.log
*.out
*.err
.env
.venv
venv/
*.bak
__quarantine__/
artifacts/
patch.last.diff
"@ | Out-File -Encoding UTF8 .gitignore

    # 4. Создаём README.md
    @"
# $Name

Проект создан Watson Agent 2.0.

## Быстрый старт

\`\`\`powershell
# Установите зависимости
pip install -r requirements.txt

# Запустите тесты
pytest -q

# Запустите приложение
py src/main.py
\`\`\`

## Структура

\`\`\`
$Name/
├── src/           # Исходный код
├── tests/         # Тесты
├── scripts/       # Утилиты и скрипты
└── README.md      # Эта документация
\`\`\`

## Watson Agent

Этот проект управляется автономным AI-агентом.
Отправляйте задачи через Telegram или Cursor Tasks.
"@ | Out-File -Encoding UTF8 README.md

    # 5. Создаём структуру каталогов
    $dirs = @('.\src', '.\tests', '.\scripts')
    if ($WithFrontend -ne 'none') {
        $dirs += '.\frontend'
    }
    New-Item -ItemType Directory -Path $dirs -Force | Out-Null
    
    # 6. Базовый main.py
    @"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
$Name - Main entry point
"""

def main():
    print("Hello from $Name!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
"@ | Out-File -Encoding UTF8 src\main.py

    # 7. Базовый тест
    @"
import pytest
from src.main import main

def test_main():
    assert main() == 0
"@ | Out-File -Encoding UTF8 tests\test_main.py

    # 8. requirements.txt
    @"
pytest>=7.0.0
requests>=2.28.0
"@ | Out-File -Encoding UTF8 requirements.txt

    # 9. pytest.ini
    @"
[pytest]
testpaths = tests
markers =
    integration: tests requiring external services
"@ | Out-File -Encoding UTF8 pytest.ini

    # 10. Frontend setup (если указан)
    if ($WithFrontend -eq 'react-vite') {
        Write-Host "`n[FRONTEND] Setting up React + Vite + TypeScript..." -ForegroundColor Cyan
        
        # package.json
        @"
{
  "name": "$($Name.ToLower())-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "playwright test",
    "test:ui": "playwright test --ui"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.40.0",
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
"@ | Out-File -Encoding UTF8 frontend\package.json

        # vite.config.ts
        @"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
"@ | Out-File -Encoding UTF8 frontend\vite.config.ts

        # tsconfig.json
        @"
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
"@ | Out-File -Encoding UTF8 frontend\tsconfig.json

        # tsconfig.node.json
        @"
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
"@ | Out-File -Encoding UTF8 frontend\tsconfig.node.json

        # index.html
        @"
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>$Name</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"@ | Out-File -Encoding UTF8 frontend\index.html

        # Создаём src внутри frontend
        New-Item -ItemType Directory -Path .\frontend\src -Force | Out-Null

        # src/main.tsx
        @"
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"@ | Out-File -Encoding UTF8 frontend\src\main.tsx

        # src/App.tsx
        @"
import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <h1>$Name</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          Count: {count}
        </button>
        <p>Built with Watson Agent 2.0</p>
      </div>
    </div>
  )
}

export default App
"@ | Out-File -Encoding UTF8 frontend\src\App.tsx

        # src/App.css
        @"
.App {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.card {
  padding: 2em;
}

button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
  background-color: #1a1a1a;
  cursor: pointer;
  transition: border-color 0.25s;
}

button:hover {
  border-color: #646cff;
}
"@ | Out-File -Encoding UTF8 frontend\src\App.css

        # src/index.css
        @"
:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;
  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

h1 {
  font-size: 3.2em;
  line-height: 1.1;
}
"@ | Out-File -Encoding UTF8 frontend\src\index.css

        # Playwright config
        @"
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
"@ | Out-File -Encoding UTF8 frontend\playwright.config.ts

        # E2E smoke test
        New-Item -ItemType Directory -Path .\frontend\e2e -Force | Out-Null
        @"
import { test, expect } from '@playwright/test';

test('homepage renders and button works', async ({ page }) => {
  await page.goto('/');
  
  // Check title
  await expect(page.locator('h1')).toContainText('$Name');
  
  // Check initial button text
  const button = page.locator('button');
  await expect(button).toContainText('Count: 0');
  
  // Click button
  await button.click();
  await expect(button).toContainText('Count: 1');
  
  // Click again
  await button.click();
  await expect(button).toContainText('Count: 2');
});
"@ | Out-File -Encoding UTF8 frontend\e2e\smoke.spec.ts

        # Run scripts
        @"
#!/usr/bin/env pwsh
# Run-Frontend.ps1 - Start Vite dev server

Push-Location `$PSScriptRoot\..\frontend
try {
    if (-not (Test-Path node_modules)) {
        Write-Host "[FRONTEND] Installing dependencies..." -ForegroundColor Cyan
        npm install
    }
    Write-Host "[FRONTEND] Starting Vite dev server on :3000..." -ForegroundColor Green
    npm run dev
} finally {
    Pop-Location
}
"@ | Out-File -Encoding UTF8 scripts\Run-Frontend.ps1

        @"
#!/usr/bin/env pwsh
# Run-Backend.ps1 - Start FastAPI backend

Push-Location `$PSScriptRoot\..
try {
    if (-not (Test-Path venv)) {
        Write-Host "[BACKEND] Creating virtual environment..." -ForegroundColor Cyan
        python -m venv venv
    }
    
    `$activate = if (`$IsWindows -or `$env:OS) { ".\venv\Scripts\Activate.ps1" } else { "./venv/bin/activate" }
    . `$activate
    
    if (-not (Get-Command uvicorn -ErrorAction SilentlyContinue)) {
        Write-Host "[BACKEND] Installing dependencies..." -ForegroundColor Cyan
        pip install -r requirements.txt
    }
    
    Write-Host "[BACKEND] Starting uvicorn on :8000..." -ForegroundColor Green
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
} finally {
    Pop-Location
}
"@ | Out-File -Encoding UTF8 scripts\Run-Backend.ps1

        # Обновляем backend main.py для FastAPI (V3 с метриками)
        @"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
$Name - FastAPI Backend
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="$Name API")

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello from $Name API!"}

@app.get("/health")
def health():
    return {"ok": True, "service": "$Name"}

@app.get("/metrics")
def metrics():
    """Метрики для мониторинга (V3)"""
    return {
        "ok": True,
        "service": "$Name",
        "version": {
            "image_tag": os.getenv("IMAGE_TAG", "unknown"),
            "git_sha": os.getenv("GIT_SHA", "unknown"),
        },
        "environment": os.getenv("WATSON_PROFILE", "local")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"@ | Out-File -Encoding UTF8 src\main.py

        # Обновляем requirements.txt
        @"
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pytest>=7.0.0
requests>=2.28.0
"@ | Out-File -Encoding UTF8 requirements.txt

        Write-Host "[FRONTEND] React + Vite + TypeScript + Playwright setup complete!" -ForegroundColor Green
    }

    # 11. Docker setup
    Write-Host "`n[DOCKER] Creating Dockerfile and compose..." -ForegroundColor Cyan
    
    # Backend Dockerfile
    @"
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/
COPY tests/ ./tests/

# Expose port
EXPOSE 8000

# Run app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
"@ | Out-File -Encoding UTF8 Dockerfile

    # Frontend Dockerfile (если есть)
    if ($WithFrontend -eq 'react-vite') {
        @"
FROM node:20-alpine as builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"@ | Out-File -Encoding UTF8 frontend\Dockerfile

        # nginx.conf для фронтенда
        @"
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files `$uri `$uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
    }
}
"@ | Out-File -Encoding UTF8 frontend\nginx.conf
    }

    # docker-compose.yml
    $composeContent = @"
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
    environment:
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
"@

    if ($WithFrontend -eq 'react-vite') {
        $composeContent += @"

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
"@
    }

    $composeContent | Out-File -Encoding UTF8 docker-compose.yml

    # .dockerignore
    @"
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
*.log
*.out
*.err
.env
.venv
venv/
.git
.gitignore
*.md
Dockerfile
docker-compose.yml
"@ | Out-File -Encoding UTF8 .dockerignore

    if ($WithFrontend -eq 'react-vite') {
        @"
node_modules/
dist/
.git
*.log
"@ | Out-File -Encoding UTF8 frontend\.dockerignore
    }

    # Docker run script
    @"
#!/usr/bin/env pwsh
# Run-Docker.ps1 - Start all services with docker-compose

Write-Host "[DOCKER] Building and starting services..." -ForegroundColor Cyan

docker-compose up --build -d

Write-Host "[DOCKER] Services started!" -ForegroundColor Green
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor Cyan
$(if ($WithFrontend -eq 'react-vite') { "Write-Host `"   Frontend: http://localhost:3000`" -ForegroundColor Cyan" })

Write-Host "`n[DOCKER] Logs: docker-compose logs -f"
Write-Host "[DOCKER] Stop:  docker-compose down`n"
"@ | Out-File -Encoding UTF8 scripts\Run-Docker.ps1

    Write-Host "[DOCKER] Docker setup complete!" -ForegroundColor Green

    # 12. Pre-commit hooks setup
    Write-Host "`n[CI] Setting up pre-commit hooks..." -ForegroundColor Cyan
    
    # .pre-commit-config.yaml
    @"
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=120", "--extend-ignore=E203,W503"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
        args: ["--ignore-missing-imports", "--no-strict-optional"]
"@ | Out-File -Encoding UTF8 .pre-commit-config.yaml

    # setup.cfg для конфигурации линтеров
    @"
[flake8]
max-line-length = 120
extend-ignore = E203, W503
exclude = .git,__pycache__,venv,.venv,build,dist

[isort]
profile = black
line_length = 120
skip = .git,__pycache__,venv,.venv,build,dist

[mypy]
ignore_missing_imports = True
no_strict_optional = True
warn_return_any = False
warn_unused_configs = True
"@ | Out-File -Encoding UTF8 setup.cfg

    # Run-CI.ps1
    @"
#!/usr/bin/env pwsh
# Run-CI.ps1 - Full CI pipeline: lint + test + e2e

param(
    [switch]`$SkipTests,
    [switch]`$SkipE2E,
    [switch]`$AutoFix
)

`$ErrorActionPreference = 'Continue'
`$exitCode = 0

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Watson CI Pipeline" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Linting
Write-Host "[LINT] Running black..." -ForegroundColor Yellow
if (`$AutoFix) {
    black src tests
} else {
    black --check src tests
    if (`$LASTEXITCODE -ne 0) { `$exitCode = 1 }
}

Write-Host "`n[LINT] Running isort..." -ForegroundColor Yellow
if (`$AutoFix) {
    isort src tests
} else {
    isort --check-only src tests
    if (`$LASTEXITCODE -ne 0) { `$exitCode = 1 }
}

Write-Host "`n[LINT] Running flake8..." -ForegroundColor Yellow
flake8 src tests
if (`$LASTEXITCODE -ne 0) { `$exitCode = 1 }

Write-Host "`n[LINT] Running mypy..." -ForegroundColor Yellow
mypy src
if (`$LASTEXITCODE -ne 0) { `$exitCode = 1 }

# 2. Unit tests
if (-not `$SkipTests) {
    Write-Host "`n[TEST] Running pytest..." -ForegroundColor Yellow
    pytest -v --tb=short
    if (`$LASTEXITCODE -ne 0) { `$exitCode = 1 }
}

# 3. E2E tests (if frontend exists)
if ((-not `$SkipE2E) -and (Test-Path frontend)) {
    Write-Host "`n[E2E] Running Playwright..." -ForegroundColor Yellow
    Push-Location frontend
    try {
        if (-not (Test-Path node_modules)) {
            npm install
        }
        npm test -- --reporter=list
        if (`$LASTEXITCODE -ne 0) { `$exitCode = 1 }
    } finally {
        Pop-Location
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
if (`$exitCode -eq 0) {
    Write-Host "  CI PASSED" -ForegroundColor Green
} else {
    Write-Host "  CI FAILED" -ForegroundColor Red
}
Write-Host "========================================`n" -ForegroundColor Cyan

exit `$exitCode
"@ | Out-File -Encoding UTF8 scripts\Run-CI.ps1

    # Install pre-commit hooks script
    @"
#!/usr/bin/env pwsh
# Install-Hooks.ps1 - Install pre-commit hooks

Write-Host "[HOOKS] Installing pre-commit hooks..." -ForegroundColor Cyan

# Check if pre-commit is installed
if (-not (Get-Command pre-commit -ErrorAction SilentlyContinue)) {
    Write-Host "[HOOKS] Installing pre-commit..." -ForegroundColor Yellow
    pip install pre-commit
}

# Install hooks
pre-commit install

Write-Host "[HOOKS] Pre-commit hooks installed!" -ForegroundColor Green
Write-Host "[HOOKS] Run manually: pre-commit run --all-files`n"
"@ | Out-File -Encoding UTF8 scripts\Install-Hooks.ps1

    # Обновляем requirements.txt с dev зависимостями
    $reqContent = Get-Content requirements.txt -Raw
    $reqContent += @"

# Development
black>=23.12.0
isort>=5.13.0
flake8>=7.0.0
mypy>=1.7.0
pre-commit>=3.5.0
"@
    $reqContent | Out-File -Encoding UTF8 requirements.txt

    Write-Host "[CI] Pre-commit and CI setup complete!" -ForegroundColor Green

    # 13. Terraform scaffold
    Write-Host "`n[IaC] Creating Terraform scaffold..." -ForegroundColor Cyan
    
    New-Item -ItemType Directory -Path .\terraform -Force | Out-Null
    
    # main.tf
    @"
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

# Example: Local file resource
resource "local_file" "deployment_info" {
  filename = "`${path.module}/deployment.json"
  content = jsonencode({
    project_name = "$Name"
    deployed_at  = timestamp()
    environment  = var.environment
  })
}

output "deployment_info" {
  value = local_file.deployment_info.filename
}
"@ | Out-File -Encoding UTF8 terraform\main.tf

    # variables.tf
    @"
variable "environment" {
  description = "Deployment environment (local/staging/prod)"
  type        = string
  default     = "local"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "$Name"
}

variable "region" {
  description = "Deployment region (for cloud providers)"
  type        = string
  default     = "us-east-1"
}
"@ | Out-File -Encoding UTF8 terraform\variables.tf

    # outputs.tf
    @"
output "project_name" {
  description = "The name of the project"
  value       = var.project_name
}

output "environment" {
  description = "Deployment environment"
  value       = var.environment
}
"@ | Out-File -Encoding UTF8 terraform\outputs.tf

    # terraform.tfvars.example
    @"
# Example Terraform variables
# Copy to terraform.tfvars and customize

environment  = "local"
project_name = "$Name"

# For cloud deployments:
# region = "us-east-1"
# instance_type = "t3.micro"
"@ | Out-File -Encoding UTF8 terraform\terraform.tfvars.example

    # .gitignore для terraform
    @"
# Terraform
.terraform/
*.tfstate
*.tfstate.*
.terraform.lock.hcl
terraform.tfvars
"@ | Out-File -Encoding UTF8 terraform\.gitignore

    # README.md для terraform
    @"
# Terraform Infrastructure

## Quick Start

\`\`\`bash
# Initialize
terraform init

# Plan
terraform plan

# Apply
terraform apply

# Destroy
terraform destroy
\`\`\`

## Variables

See \`terraform.tfvars.example\` for available variables.

## State Management

For production, configure remote state in \`main.tf\`:

\`\`\`hcl
terraform {
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "$Name/terraform.tfstate"
    region = "us-east-1"
  }
}
\`\`\`

## Next Steps

1. Add cloud provider resources (AWS/Azure/GCP)
2. Configure networking
3. Set up monitoring and alerts
4. Implement CI/CD pipelines
"@ | Out-File -Encoding UTF8 terraform\README.md

    Write-Host "[IaC] Terraform scaffold created!" -ForegroundColor Green

    # 14. Staging deployment (V3)
    Write-Host "`n[DEPLOY] Creating staging deployment files..." -ForegroundColor Cyan
    
    # docker-compose.staging.yml
    @"
version: '3.9'
services:
  backend:
    image: `${REGISTRY_URL}/`${REGISTRY_NS}/${($Name.ToLower() -replace '[^a-z0-9_-]','_')}_backend:`${IMAGE_TAG}
    env_file: .env.staging
    ports:
      - "`${BACKEND_PORT:-8080}:8080"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8080/health"]
      interval: 10s
      timeout: 3s
      retries: 5
$(if ($WithFrontend -eq 'react-vite') {@"

  frontend:
    image: `${REGISTRY_URL}/`${REGISTRY_NS}/${($Name.ToLower() -replace '[^a-z0-9_-]','_')}_frontend:`${IMAGE_TAG}
    env_file: .env.staging
    ports:
      - "`${FRONTEND_PORT:-5173}:5173"
    depends_on:
      - backend
    restart: unless-stopped
"@ })
"@ | Out-File -Encoding UTF8 docker-compose.staging.yml

    # .env.staging.example
    @"
IMAGE_TAG=latest
BACKEND_PORT=8080
FRONTEND_PORT=5173
API_BASE=http://localhost:8080
"@ | Out-File -Encoding UTF8 .env.staging.example

    # Ansible infrastructure
    New-Item -ItemType Directory -Path .\infra\ansible\inventory -Force | Out-Null
    
    # inventory/staging
    @"
[staging]
`${STAGING_SSH_HOST}
"@ | Out-File -Encoding UTF8 infra\ansible\inventory\staging

    # playbook.yml
    @"
---
- hosts: staging
  become: true
  vars:
    project_slug: "${($Name.ToLower() -replace '[^a-z0-9_-]','_')}"
    deploy_path: "`{{ deploy_path | default('/opt/apps/' ~ project_slug) }}"
    backend_port: "`{{ backend_port | default('8080') }}"
  
  tasks:
    - name: Ensure deploy path exists
      file:
        path: "`{{ deploy_path }}"
        state: directory
        mode: '0755'
    
    - name: Upload compose file
      copy:
        src: "`{{ playbook_dir }}/../../docker-compose.staging.yml"
        dest: "`{{ deploy_path }}/docker-compose.yml"
        mode: '0644'
    
    - name: Upload env file template if missing
      copy:
        src: "`{{ playbook_dir }}/../../.env.staging.example"
        dest: "`{{ deploy_path }}/.env"
        force: no
        mode: '0644'
    
    - name: Pull and start containers
      community.docker.docker_compose_v2:
        project_src: "`{{ deploy_path }}"
        state: present
        pull: always
    
    - name: Wait for backend health
      uri:
        url: "http://localhost:`{{ backend_port }}/health"
        return_content: yes
        status_code: 200
      register: health_check
      retries: 10
      delay: 3
      until: health_check.status == 200
    
    - name: Print health check result
      debug:
        msg: "`{{ health_check.content }}"
"@ | Out-File -Encoding UTF8 infra\ansible\playbook.yml

    # ansible.cfg
    @"
[defaults]
host_key_checking = False
inventory = inventory/staging
remote_user = `${STAGING_SSH_USER}
private_key_file = ~/.ssh/id_rsa

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
"@ | Out-File -Encoding UTF8 infra\ansible\ansible.cfg

    # infra/README.md
    @"
# Infrastructure - Staging Deploy

## Prerequisites

1. Ansible installed: \`pip install ansible-core ansible-lint\`
2. Collection: \`ansible-galaxy collection install community.docker\`
3. SSH access to staging server
4. Docker + Docker Compose installed on staging server

## Setup

### 1. Create \`.env.staging\` on server

SSH to staging and create \`/opt/apps/$($Name.ToLower() -replace '[^a-z0-9_-]','_')/.env\`:

\`\`\`bash
IMAGE_TAG=latest
REGISTRY_URL=registry.example.com
REGISTRY_NS=watson
BACKEND_PORT=8080
FRONTEND_PORT=5173
\`\`\`

### 2. Update inventory

Edit \`infra/ansible/inventory/staging\` with your server IP:

\`\`\`ini
[staging]
192.168.1.100
\`\`\`

## Deploy

\`\`\`bash
cd infra/ansible

# Test connection
ansible staging -m ping

# Deploy
ansible-playbook playbook.yml

# Deploy with custom vars
ansible-playbook playbook.yml -e "deploy_path=/custom/path" -e "backend_port=9000"
\`\`\`

## Health Check

\`\`\`bash
curl http://<staging-ip>:8080/health
curl http://<staging-ip>:8080/metrics
\`\`\`

## Rollback

On staging server:

\`\`\`bash
cd /opt/apps/$($Name.ToLower() -replace '[^a-z0-9_-]','_')
# Edit .env and change IMAGE_TAG to previous version
vi .env
# Pull and restart
docker compose pull
docker compose up -d
\`\`\`

## Logs

\`\`\`bash
cd /opt/apps/$($Name.ToLower() -replace '[^a-z0-9_-]','_')
docker compose logs -f --tail=200
\`\`\`

## CI/CD Integration

See \`.github/workflows/ci-cd.yml\` for automated deployment pipeline.

Required GitHub Secrets:
- REGISTRY_URL, REGISTRY_NS, REGISTRY_USER, REGISTRY_PASS
- SSH_KEY_B64 (base64 encoded private key)
- STAGING_SSH_HOST, STAGING_SSH_USER
- (optional) TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
"@ | Out-File -Encoding UTF8 infra\README.md

    Write-Host "[DEPLOY] Staging deployment files created!" -ForegroundColor Green

    # 15. Первый коммит
    git add -A
    git commit -m "init: Watson project $Name$(if ($WithFrontend -ne 'none') { " with $WithFrontend frontend" })"

    Write-Host "`n[PROJECT] Created successfully!" -ForegroundColor Green
    Write-Host "   Path: $projectPath" -ForegroundColor Cyan
    Write-Host "`n[NEXT] Steps:" -ForegroundColor Yellow
    Write-Host "   1. cd $projectPath"
    if ($WithFrontend -ne 'none') {
        Write-Host "   2. Backend:  pwsh scripts\Run-Backend.ps1"
        Write-Host "   3. Frontend: pwsh scripts\Run-Frontend.ps1"
        Write-Host "   4. E2E:      cd frontend && npm test"
    } else {
        Write-Host "   2. Open in Cursor"
        Write-Host "   3. Start Watson API"
    }
    Write-Host "   5. Send tasks via Telegram or Cursor Tasks`n"

} finally {
    Pop-Location
}

