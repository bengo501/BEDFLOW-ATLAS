# Conteinerização (Docker) do BEDFLOW-ATLAS

Documentação da conteinerização do projeto: **objetivos**, **como foi criada**,
**decisões de design**, **como usar** e **como atualizar**.

> TL;DR — a partir desta pasta:
> ```bash
> cp .env.example .env          # ajuste se quiser
> docker compose up -d --build  # sobe a stack
> # backend: http://localhost:8000/docs   frontend: http://localhost:5173
> docker compose down           # encerra
> ```

---

## 1. Objetivos

- **Reprodutibilidade**: o trabalho depende de Python, ANTLR, OpenFOAM e Blender
  com versões específicas. O container fixa esse ambiente e elimina o clássico
  "na minha máquina funciona".
- **Subir tudo com um comando**: backend (API FastAPI), frontend (Vite/React) e
  a infraestrutura (PostgreSQL, Redis, MinIO) num único `docker compose up`.
- **Onboarding rápido**: avaliar/rodar o projeto sem instalar Python, Node,
  Postgres etc. no host.
- **Base para CI/deploy**: a mesma imagem usada localmente pode rodar em CI
  (`.github/workflows/docker-image.yml`) e, futuramente, num servidor.

## 2. Arquitetura da stack

`docker compose` orquestra 5 serviços:

| Serviço | Imagem | Papel | Porta (host) |
|---------|--------|-------|--------------|
| `backend` | build `docker/Dockerfile` | API FastAPI + motor de modelagem (python) | 8000 |
| `frontend` | build `docker/Dockerfile.frontend` | UI React/Vite (dev server) | 5173 |
| `postgres` | `postgres:15` | banco relacional | 5432 |
| `redis` | `redis:7-alpine` | cache/fila | 6379 |
| `minio` | `minio/minio` | armazenamento de objetos (S3) | 9000/9001 |

O frontend faz proxy de `/api`, `/files`, `/generated` para o backend
(`VITE_PROXY_TARGET=http://backend:8000`). Dados de Postgres/Redis/MinIO ficam em
**volumes nomeados** (persistem entre `up`/`down`).

## 3. Como foi criada (arquivos e decisões de design)

### Arquivos

| Arquivo | Função |
|---------|--------|
| [`docker/Dockerfile`](Dockerfile) | imagem do backend (multi-perfil) |
| [`docker/Dockerfile.frontend`](Dockerfile.frontend) | imagem do frontend (Vite) |
| [`docker/docker-compose.yml`](docker-compose.yml) | orquestra os 5 serviços |
| [`docker/requirements-extra.txt`](requirements-extra.txt) | deps extra só do container |
| [`docker/.env.example`](.env.example) | modelo de configuração (copie para `.env`) |
| [`docker/docker-setup.sh`](docker-setup.sh) / [`.bat`](docker-setup.bat) | atalho de setup |
| [`.dockerignore`](../.dockerignore) | exclui `node_modules`, `.git`, `generated`… do build |

### Decisões de design (e os porquês)

1. **Imagem leve por padrão (`WITH_BLENDER=0`, `WITH_OPENFOAM=0`)**
   O Blender e o OpenFOAM tornam o build lento e a imagem enorme. Como o **motor
   de modelagem em python** (`scripts/python_modeling`) faz a geração de malha sem
   Blender, o default é uma imagem **leve (~650 MB), rápida de construir e
   testar**. Com Blender a imagem vai a **~2.7 GB** (a camada do Blender 4.0 sozinha
   ≈ 1.55 GB). Blender/OpenFOAM são **opcionais** via build-arg.

2. **`.dockerignore`** — o contexto de build é a raiz do repo. Sem ele, o Docker
   enviaria `frontend/node_modules`, `.git`, `generated/`, `local_data/`… ao
   daemon, deixando o build lento e a imagem suja.

3. **Camadas em ordem de cache** — primeiro `requirements*.txt` + `pip install`,
   depois o código. Mudar código **não** reinstala as dependências.

4. **`requirements-extra.txt` separado** — `psycopg2-binary` (driver Postgres),
   `numpy`/`scipy`/`trimesh`/`manifold3d` (motor python: DEM, booleanos m2/m3,
   export glTF) e `antlr4-python3-runtime` (compilador `.bed`) ficam **só na
   imagem**, sem pesar o fluxo local (que usa SQLite).

5. **`HEALTHCHECK`** batendo em `/health` (faz `SELECT 1` no banco) para o compose
   saber quando o backend está realmente pronto.

### Bugs do setup antigo corrigidos nesta conteinerização

Durante a construção, validei a imagem rodando de verdade e corrigi:

| Problema (antes) | Efeito | Correção |
|------------------|--------|----------|
| **sem `.dockerignore`** | build lento; contexto gigante | adicionado |
| **`psycopg2` comentado** | backend não conectava no Postgres configurado | instalado via `requirements-extra` |
| **`bedflow_*.py` da raiz não copiados** | `import bedflow_local_paths` falhava fora do compose | `COPY` desses módulos |
| **`scipy` ausente** | trimesh 4.12 quebrava nos booleanos → **m2/m3 falhavam em silêncio** | `scipy` adicionado |
| **proxy do Vite em `localhost:8000`** | frontend no container não achava o backend | `VITE_PROXY_TARGET=http://backend:8000` |
| **`apt-key` (deprecado) + OpenFOAM sempre instalado** | build frágil/lento | OpenFOAM opcional + keyring `signed-by` |
| **Blender sem libs de runtime** | binário não rodava headless | libs X/GL instaladas quando `WITH_BLENDER=1` |

## 4. Como usar

### 4.1 Stack completa (recomendado)

```bash
cd docker
cp .env.example .env
docker compose up -d --build
```

Acesse:
- **API**: http://localhost:8000  (Swagger em `/docs`)
- **Frontend**: http://localhost:5173
- **MinIO console**: http://localhost:9001

```bash
docker compose logs -f          # ver logs
docker compose ps               # status
docker compose down             # parar (mantém volumes/dados)
docker compose down -v          # parar e APAGAR os dados (postgres/redis/minio)
```

### 4.2 Só o backend, leve, com SQLite (sem Postgres/infra)

A imagem leve roda sozinha com SQLite (sem precisar de Postgres):

```bash
docker build -f docker/Dockerfile -t bedflow-backend:light .
docker run --rm -p 8000:8000 bedflow-backend:light
curl http://localhost:8000/health
```

> Validado: `/health` retorna `database: connected` e o motor python
> (numpy/scipy/trimesh/manifold3d) gera malha m1/m2/m3 dentro do container.

### 4.3 Incluir Blender / OpenFOAM

No `docker/.env`:
```dotenv
WITH_BLENDER=1
MODELING_PROFILE=blender
# WITH_OPENFOAM=1   # best-effort em base debian; CFD também roda via WSL no host
```
Depois `docker compose up -d --build` (o build fica bem mais lento por baixar o
Blender). Ou, num build direto:
```bash
docker build -f docker/Dockerfile --build-arg WITH_BLENDER=1 -t bedflow-backend:blender .
```

> Validado: a imagem com Blender (~2.7 GB) tem o **Blender 4.0.0** rodando headless
> (`blender --version`), e o pipeline real gera o leito dentro do container:
> ```bash
> docker run --rm bedflow-backend:blender \
>   blender --background --python /workspace/scripts/blender_scripts/leito_extracao.py -- \
>   --params /workspace/dsl/wizard_templates/_test_bed_m1_hollow_boolean.json \
>   --output /tmp/m1.blend --formats blend,stl
> # -> "modelo 3d gerado com sucesso!" (gera m1.blend + m1.stl)
> ```

### 4.4 SQLite vs Postgres no compose

Por padrão o compose usa Postgres. Para usar SQLite (mais simples), no `.env`:
```dotenv
DATABASE_URL=sqlite:////workspace/local_data/cfd_pipeline.db
```

### Atalho de setup

`./docker-setup.sh` (Linux/Git-Bash) ou `docker-setup.bat` (Windows) fazem
`.env` + `compose up -d --build` + checagem do `/health`.

## 5. Como atualizar

- **Mudou o código** (com o bind-mount do compose, o backend recarrega sozinho via
  `--reload`). Sem bind-mount, reconstrua: `docker compose build backend`.
- **Mudou `requirements.txt` / `requirements-extra.txt`**:
  ```bash
  docker compose build --no-cache backend   # garante reinstalar as deps
  docker compose up -d
  ```
- **Atualizar imagens base** (python, postgres…):
  ```bash
  docker compose pull          # postgres/redis/minio
  docker compose build --pull  # backend/frontend (refaz a base python/node)
  ```
- **Limpeza** (recuperar espaço):
  ```bash
  docker compose down -v       # remove containers + volumes (apaga dados!)
  docker image prune -f        # remove imagens soltas
  docker builder prune -f      # limpa cache de build
  ```
- **Mudar versão do Blender**: `--build-arg BLENDER_VERSION=4.0.2` (ajuste também a
  URL no `Dockerfile` se mudar de série, ex. Blender4.1).

## 6. Solução de problemas

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| build falha em `docker/dockerfile:1` / `docker-credential-*` | helper de credenciais fora do PATH (git-bash) | use o PowerShell/CMD, ou adicione `C:\Program Files\Docker\Docker\resources\bin` ao PATH |
| `database disconnected` no `/health` | Postgres ainda subindo ou `DATABASE_URL` errado | aguarde o healthcheck; confira o `.env` |
| frontend abre mas chamadas `/api` falham | proxy não aponta pro backend | confirme `VITE_PROXY_TARGET=http://backend:8000` |
| m2/m3 saem sem furos/partículas no container | faltou `scipy`/`manifold3d` | já incluídos em `requirements-extra.txt`; rebuild `--no-cache` |
| porta ocupada (8000/5173/5432…) | outro serviço no host | mude as portas no `.env` (`BACKEND_PORT` etc.) |

## 7. Referência — variáveis de ambiente (`docker/.env`)

| Variável | Default | Descrição |
|----------|---------|-----------|
| `WITH_BLENDER` | `0` | inclui Blender na imagem do backend |
| `WITH_OPENFOAM` | `0` | tenta incluir OpenFOAM (best-effort) |
| `MODELING_PROFILE` | `python` | motor em runtime (`python`/`blender`) |
| `DATABASE_URL` | postgres do compose | string de conexão do banco |
| `POSTGRES_DB/USER/PASSWORD` | `cfd_pipeline`/`postgres`/`postgres123` | credenciais do Postgres |
| `MINIO_ROOT_USER/PASSWORD` | `minioadmin`/`minioadmin123` | credenciais do MinIO |
| `SEED_DEMO_DATA` | `1` | popula dados demo no 1º arranque |
| `BACKEND_PORT`/`FRONTEND_PORT`/… | 8000/5173/… | portas publicadas no host |
| `IMAGE_TAG` | `local` | tag das imagens construídas |

---

> Nota: por uma regra do `.gitignore` (`*.md`), este `README.md` pode precisar de
> `git add -f docker/README.md` para ser versionado.
