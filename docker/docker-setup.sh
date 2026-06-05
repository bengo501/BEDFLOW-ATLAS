#!/bin/bash
# setup da stack docker do BEDFLOW-ATLAS (rode a partir da pasta docker/)
set -e

echo "========================================"
echo "   BEDFLOW-ATLAS - DOCKER SETUP"
echo "========================================"
echo

echo "[1/4] verificando docker..."
if ! command -v docker >/dev/null 2>&1; then
    echo "erro: docker nao encontrado! instale: https://docs.docker.com/get-docker/"
    exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
    echo "erro: 'docker compose' (v2) nao disponivel. atualize o Docker Desktop/Engine."
    exit 1
fi
echo "docker + compose v2 ok"

echo
echo "[2/4] preparando docker/.env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env criado a partir de .env.example (ajuste se necessario)"
else
    echo ".env ja existe"
fi

echo
echo "[3/4] subindo a stack (build + up -d)..."
# perfil leve por default (WITH_BLENDER=0); para incluir blender: WITH_BLENDER=1 no .env
docker compose up -d --build

echo
echo "[4/4] aguardando o backend ficar saudavel..."
for i in $(seq 1 30); do
    if curl -fsS "http://localhost:${BACKEND_PORT:-8000}/health" >/dev/null 2>&1; then
        echo "backend saudavel."
        break
    fi
    sleep 3
done

echo
echo "========================================"
echo "   STACK NO AR!"
echo "========================================"
echo "- frontend:    http://localhost:${FRONTEND_PORT:-5173}"
echo "- backend:     http://localhost:${BACKEND_PORT:-8000}  (/docs para a API)"
echo "- postgres:    localhost:${POSTGRES_PORT:-5432}"
echo "- redis:       localhost:${REDIS_PORT:-6379}"
echo "- minio:       http://localhost:${MINIO_PORT:-9000}  (console :${MINIO_CONSOLE_PORT:-9001})"
echo
echo "logs:  docker compose logs -f"
echo "parar: docker compose down"
echo
