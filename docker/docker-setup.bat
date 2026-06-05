@echo off
chcp 65001 >nul
REM setup da stack docker do BEDFLOW-ATLAS (rode a partir da pasta docker\)
echo ========================================
echo   BEDFLOW-ATLAS - DOCKER SETUP
echo ========================================
echo.

echo [1/4] verificando docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo erro: docker nao encontrado! instale o Docker Desktop.
    pause
    exit /b 1
)
docker compose version >nul 2>&1
if errorlevel 1 (
    echo erro: "docker compose" (v2) nao disponivel. atualize o Docker Desktop.
    pause
    exit /b 1
)
echo docker + compose v2 ok

echo.
echo [2/4] preparando docker\.env...
if not exist .env (
    copy .env.example .env >nul
    echo .env criado a partir de .env.example
) else (
    echo .env ja existe
)

echo.
echo [3/4] subindo a stack (build + up -d)...
docker compose up -d --build

echo.
echo [4/4] stack iniciada.
echo ========================================
echo   STACK NO AR!
echo ========================================
echo - frontend:    http://localhost:5173
echo - backend:     http://localhost:8000   (/docs para a API)
echo - postgres:    localhost:5432
echo - redis:       localhost:6379
echo - minio:       http://localhost:9000   (console :9001)
echo.
echo logs:  docker compose logs -f
echo parar: docker compose down
echo.
pause
