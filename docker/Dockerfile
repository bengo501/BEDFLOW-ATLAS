# =============================================================================
# imagem do BACKEND (FastAPI + motor de modelagem em python)
# contexto de build = RAIZ do repositorio:
#   docker build -f docker/Dockerfile -t bedflow-backend .
#
# perfis (build-args):
#   - LEVE (default): WITH_BLENDER=0 WITH_OPENFOAM=0  -> build rapido, so motor python
#   - com blender:    --build-arg WITH_BLENDER=1
#   - com openfoam:   --build-arg WITH_OPENFOAM=1   (best-effort em base debian)
# =============================================================================
FROM python:3.11-slim AS base

# toggles de build (default = imagem LEVE, sem blender/openfoam)
ARG WITH_BLENDER=0
ARG WITH_OPENFOAM=0
ARG BLENDER_VERSION=4.0.0

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/workspace \
    PIP_NO_CACHE_DIR=1 \
    WITH_BLENDER=${WITH_BLENDER} \
    WITH_OPENFOAM=${WITH_OPENFOAM} \
    MODELING_PROFILE=python

WORKDIR /workspace

# dependencias de sistema minimas (curl p/ healthcheck e toggles; xz p/ blender)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl xz-utils \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------------------------
# dependencias python — camada cacheada (so refaz quando os requirements mudam)
# ----------------------------------------------------------------------------
COPY backend/requirements.txt /tmp/req-backend.txt
COPY docker/requirements-extra.txt /tmp/req-extra.txt
RUN pip install --upgrade pip \
    && pip install -r /tmp/req-backend.txt -r /tmp/req-extra.txt

# ----------------------------------------------------------------------------
# OpenFOAM (opcional) — repo oficial e para ubuntu; em debian-slim e best-effort.
# o pipeline CFD tambem pode rodar via WSL/host fora do container.
# ----------------------------------------------------------------------------
RUN if [ "$WITH_OPENFOAM" = "1" ]; then \
        set -eux; \
        curl -fsSL https://dl.openfoam.org/gpg.key -o /usr/share/keyrings/openfoam.asc; \
        echo "deb [signed-by=/usr/share/keyrings/openfoam.asc] http://dl.openfoam.org/ubuntu focal main" \
            > /etc/apt/sources.list.d/openfoam.list; \
        apt-get update; \
        apt-get install -y --no-install-recommends openfoam11 \
            || echo "aviso: openfoam11 nao instalou na base debian; use WSL/imagem ubuntu"; \
        rm -rf /var/lib/apt/lists/*; \
    fi
ENV PATH="/opt/openfoam11/platforms/linux64GccDPInt32Opt/bin:${PATH}"

# ----------------------------------------------------------------------------
# Blender (opcional) — inclui libs de runtime para rodar headless (--background)
# ----------------------------------------------------------------------------
RUN if [ "$WITH_BLENDER" = "1" ]; then \
        set -eux; \
        apt-get update; \
        apt-get install -y --no-install-recommends \
            libx11-6 libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1 libxkbcommon0 libsm6; \
        rm -rf /var/lib/apt/lists/*; \
        curl -fsSL "https://download.blender.org/release/Blender4.0/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
            -o /tmp/blender.tar.xz; \
        mkdir -p /opt/blender; \
        tar -xf /tmp/blender.tar.xz -C /opt/blender --strip-components=1; \
        rm /tmp/blender.tar.xz; \
    fi
ENV PATH="/opt/blender:${PATH}"

# ----------------------------------------------------------------------------
# codigo da aplicacao (apos as deps p/ aproveitar o cache de camadas)
# ----------------------------------------------------------------------------
COPY backend /workspace/backend
COPY scripts /workspace/scripts
COPY dsl /workspace/dsl
COPY tools /workspace/tools
# modulos python da RAIZ do repo, importados pelo backend (ex.: bedflow_local_paths)
COPY bedflow_local_paths.py bedflow_bed_registry.py bedflow_export_metadata.py \
     bedflow_mesh_metadata.py bedflow_viewer_hints.py bed_wizard.py /workspace/

# pastas de runtime (tambem sobrepostas por volumes no compose)
RUN mkdir -p /workspace/local_data /workspace/generated /workspace/output /workspace/logs

EXPOSE 8000

# health de infraestrutura (a rota /health faz SELECT 1 no banco)
HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
