# router grande que cobre entidades sql beds simulations results
# tambem agrega consultas para dashboard e painel admin da base
# depende de crud para sql e de results service para ler json em disco
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from backend.app.database.connection import get_db, DATABASE_URL
from backend.app.database import crud, schemas, models
from backend.app.api.deps_user import get_active_user_id
from backend.app.api.models import (
    AdminPanelEventCreate,
    DatabasePanelCounts,
    DatabasePanelEventOut,
    DatabasePanelResponse,
)
from backend.app.services.results_service import ResultsService
from backend.app.services.unified_data_service import UnifiedDataService
from backend.app.utils.pagination import (
    build_paginated_payload,
    clean_filters,
    parse_datetime_filter,
    resolve_page_limit,
)

router = APIRouter()
results_service = ResultsService()
unified_data_service = UnifiedDataService()


# ==================== ENDPOINTS BEDS ====================

@router.post("/beds", response_model=schemas.BedResponse, tags=["database", "beds"])
async def create_bed(
    bed: schemas.BedCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    criar novo leito no banco de dados
    """
    # nome e chave humana entao rejeitamos duplicado cedo
    # verificar se ja existe leito com esse nome
    existing = crud.BedCRUD.get_by_name_for_user(db, bed.name, user_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"leito com nome '{bed.name}' ja existe"
        )
    
    try:
        db_bed = crud.BedCRUD.create(db, bed, user_id=user_id)
        return db_bed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao criar leito: {str(e)}")


@router.get("/beds", response_model=schemas.BedListResponse, tags=["database", "beds"])
async def list_beds(
    page: int = Query(1, ge=1, description="numero da pagina"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="items por pagina"),
    per_page: Optional[int] = Query(None, ge=1, le=100, description="alias legado de limit"),
    search: Optional[str] = Query(None, description="buscar por nome ou descricao"),
    packing_method: Optional[str] = Query(None, description="filtrar por metodo de geracao"),
    created_from: Optional[str] = Query(None, description="filtrar por data inicial"),
    created_to: Optional[str] = Query(None, description="filtrar por data final"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    listar leitos com paginacao e busca opcional
    """
    try:
        page, limit, skip = resolve_page_limit(page=page, limit=limit, per_page=per_page)
        parsed_from = parse_datetime_filter(created_from)
        parsed_to = parse_datetime_filter(created_to, end_of_day=True)
        beds, total = crud.BedCRUD.list_filtered(
            db,
            skip=skip,
            limit=limit,
            user_id=user_id,
            search=search,
            packing_method=packing_method,
            created_from=parsed_from,
            created_to=parsed_to,
        )
        return schemas.BedListResponse(
            **build_paginated_payload(
                items=beds,
                total=total,
                page=page,
                limit=limit,
                applied_filters=clean_filters(
                    search=search,
                    packing_method=packing_method,
                    created_from=created_from,
                    created_to=created_to,
                ),
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao listar leitos: {str(e)}")


@router.get("/beds/{bed_id}", response_model=schemas.BedResponse, tags=["database", "beds"])
async def get_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    obter detalhes de um leito especifico
    """
    db_bed = crud.BedCRUD.get(db, bed_id)
    if not db_bed:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    if db_bed.user_id != user_id:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    return db_bed


@router.patch("/beds/{bed_id}", response_model=schemas.BedResponse, tags=["database", "beds"])
async def update_bed(
    bed_id: int,
    bed_update: schemas.BedUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    atualizar leito (parcial)
    """
    b0 = crud.BedCRUD.get(db, bed_id)
    if not b0 or b0.user_id != user_id:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    db_bed = crud.BedCRUD.update(db, bed_id, bed_update)
    if not db_bed:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    return db_bed


@router.delete("/beds/{bed_id}", tags=["database", "beds"])
async def delete_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    deletar leito (e todas simulacoes relacionadas em cascade)
    """
    b0 = crud.BedCRUD.get(db, bed_id)
    if not b0 or b0.user_id != user_id:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    success = crud.BedCRUD.delete(db, bed_id)
    if not success:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    return {"message": "leito deletado com sucesso", "bed_id": bed_id}


# ==================== ENDPOINTS SIMULATIONS ====================

@router.post("/simulations", response_model=schemas.SimulationResponse, tags=["database", "simulations"])
async def create_simulation(
    simulation: schemas.SimulationCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    criar nova simulacao no banco de dados
    """
    # verificar se bed existe
    bed = crud.BedCRUD.get(db, simulation.bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail=f"leito {simulation.bed_id} nao encontrado")
    if bed.user_id != user_id:
        raise HTTPException(status_code=404, detail=f"leito {simulation.bed_id} nao encontrado")
    
    try:
        db_simulation = crud.SimulationCRUD.create(db, simulation, user_id=user_id)
        return db_simulation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao criar simulacao: {str(e)}")


@router.get("/simulations", response_model=schemas.SimulationListResponse, tags=["database", "simulations"])
async def list_simulations(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(None, ge=1, le=100),
    per_page: Optional[int] = Query(None, ge=1, le=100, description="alias legado de limit"),
    bed_id: Optional[int] = Query(None, description="filtrar por leito"),
    status: Optional[str] = Query(None, description="filtrar por status"),
    search: Optional[str] = Query(None, description="filtrar por nome ou descricao"),
    regime: Optional[str] = Query(None, description="filtrar por regime"),
    solver: Optional[str] = Query(None, description="filtrar por solver"),
    created_from: Optional[str] = Query(None, description="filtrar por data inicial"),
    created_to: Optional[str] = Query(None, description="filtrar por data final"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    listar simulacoes com paginacao e filtros
    """
    try:
        page, limit, skip = resolve_page_limit(page=page, limit=limit, per_page=per_page)
        parsed_from = parse_datetime_filter(created_from)
        parsed_to = parse_datetime_filter(created_to, end_of_day=True)
        simulations, total = crud.SimulationCRUD.list_filtered(
            db,
            skip=skip,
            limit=limit,
            user_id=user_id,
            bed_id=bed_id,
            status=status,
            search=search,
            regime=regime,
            solver=solver,
            created_from=parsed_from,
            created_to=parsed_to,
        )

        return schemas.SimulationListResponse(
            **build_paginated_payload(
                items=simulations,
                total=total,
                page=page,
                limit=limit,
                applied_filters=clean_filters(
                    bed_id=bed_id,
                    status=status,
                    search=search,
                    regime=regime,
                    solver=solver,
                    created_from=created_from,
                    created_to=created_to,
                ),
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao listar simulacoes: {str(e)}")


@router.get(
    "/simulations/summary",
    tags=["database", "simulations"],
)
async def get_simulations_summary(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    resumo agregado de simulacoes.
    """
    summary = unified_data_service.get_dashboard_summary(db, user_id, recent_limit=8)
    return {
        "total": summary.total_simulations,
        "by_status": summary.by_status,
        "success_rate": summary.success_rate,
        "average_execution_time": summary.average_execution_time,
        "average_pressure_drop": summary.average_pressure_drop,
        "average_reynolds_number": summary.average_reynolds_number,
    }


@router.get(
    "/simulations/recent",
    response_model=schemas.SimulationListResponse,
    tags=["database", "simulations"],
)
async def list_recent_simulations(
    limit: int = Query(8, ge=1, le=100, description="numero maximo de simulacoes"),
    status: Optional[str] = Query(None, description="filtrar por status"),
    search: Optional[str] = Query(None, description="filtrar por nome ou descricao"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    listar as simulacoes mais recentes.
    """
    try:
        simulations, total = crud.SimulationCRUD.list_filtered(
            db,
            skip=0,
            limit=limit,
            user_id=user_id,
            status=status,
            search=search,
        )
        return schemas.SimulationListResponse(
            **build_paginated_payload(
                items=simulations,
                total=total,
                page=1,
                limit=limit,
                applied_filters=clean_filters(status=status, search=search, recent=True),
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao listar simulacoes recentes: {str(e)}")


@router.get(
    "/models-3d",
    response_model=schemas.Model3DListResponse,
    tags=["database", "models-3d"],
)
async def list_models_3d(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(None, ge=1, le=100),
    per_page: Optional[int] = Query(None, ge=1, le=100, description="alias legado de limit"),
    search: Optional[str] = Query(None, description="filtrar por nome ou descricao"),
    packing_method: Optional[str] = Query(None, description="filtrar por metodo de geracao"),
    has_blend: Optional[bool] = Query(None, description="filtrar por ficheiro blend"),
    has_stl: Optional[bool] = Query(None, description="filtrar por ficheiro stl"),
    created_from: Optional[str] = Query(None, description="filtrar por data inicial"),
    created_to: Optional[str] = Query(None, description="filtrar por data final"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    lista modelos 3d persistidos no sqlite a partir da tabela beds.
    """
    page, limit, _ = resolve_page_limit(page=page, limit=limit, per_page=per_page)
    parsed_from = parse_datetime_filter(created_from)
    parsed_to = parse_datetime_filter(created_to, end_of_day=True)
    return unified_data_service.list_models_3d(
        db,
        user_id,
        page=page,
        limit=limit,
        search=search,
        packing_method=packing_method,
        has_blend=has_blend,
        has_stl=has_stl,
        created_from=parsed_from,
        created_to=parsed_to,
    )


@router.get(
    "/history",
    response_model=schemas.HistoryResponse,
    tags=["database", "history"],
)
async def get_history(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(None, ge=1, le=200),
    per_page: Optional[int] = Query(None, ge=1, le=200, description="alias legado de limit"),
    entry_type: str = Query("all", pattern="^(all|simulation|model_3d)$"),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    packing_method: Optional[str] = Query(None),
    created_from: Optional[str] = Query(None),
    created_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    feed agregado de simulacoes e modelos 3d.
    """
    page, limit, _ = resolve_page_limit(page=page, limit=limit, per_page=per_page, max_limit=200)
    return unified_data_service.get_history(
        db,
        user_id,
        page=page,
        limit=limit,
        entry_type=entry_type,
        search=search,
        status=status,
        packing_method=packing_method,
        created_from=parse_datetime_filter(created_from),
        created_to=parse_datetime_filter(created_to, end_of_day=True),
    )


@router.get(
    "/dashboard/summary",
    response_model=schemas.DashboardSummaryResponse,
    tags=["database", "dashboard"],
)
async def get_dashboard_summary(
    recent_limit: int = Query(8, ge=1, le=50),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    resumo consolidado do dashboard com simulacoes e modelos 3d.
    """
    return unified_data_service.get_dashboard_summary(db, user_id, recent_limit=recent_limit)


@router.get(
    "/dashboard/artifacts-storage",
    response_model=schemas.ArtifactsStorageResponse,
    tags=["database", "dashboard"],
)
async def get_artifacts_storage(
    _user_id: int = Depends(get_active_user_id),
):
    """
    soma tamanhos em disco em local_data, generated e output; compara com 60 gib.
    """
    from bedflow_local_paths import get_artifacts_storage_report

    raw = get_artifacts_storage_report()
    return schemas.ArtifactsStorageResponse(
        bytes_used=raw["bytes_used"],
        bytes_cap=raw["bytes_cap"],
        cap_gb=raw["cap_gb"],
        percent_of_cap=raw["percent_of_cap"],
        breakdown=[schemas.ArtifactDirBreakdown(**row) for row in raw["breakdown"]],
    )
async def get_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    obter detalhes de uma simulacao especifica
    """
    db_simulation = crud.SimulationCRUD.get(db, simulation_id)
    if not db_simulation:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    if db_simulation.user_id != user_id:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    return db_simulation


@router.patch("/simulations/{simulation_id}", response_model=schemas.SimulationResponse, tags=["database", "simulations"])
async def update_simulation(
    simulation_id: int,
    simulation_update: schemas.SimulationUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    atualizar simulacao (ex: status, progress, metricas)
    """
    s0 = crud.SimulationCRUD.get(db, simulation_id)
    if not s0 or s0.user_id != user_id:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    db_simulation = crud.SimulationCRUD.update(db, simulation_id, simulation_update)
    if not db_simulation:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    return db_simulation


@router.delete("/simulations/{simulation_id}", tags=["database", "simulations"])
async def delete_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    deletar simulacao (e todos resultados relacionados em cascade)
    """
    s0 = crud.SimulationCRUD.get(db, simulation_id)
    if not s0 or s0.user_id != user_id:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    success = crud.SimulationCRUD.delete(db, simulation_id)
    if not success:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    return {"message": "simulacao deletada com sucesso", "simulation_id": simulation_id}


# ==================== ENDPOINTS RESULTS ====================

@router.post("/results", response_model=schemas.ResultResponse, tags=["database", "results"])
async def create_result(
    result: schemas.ResultCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    criar novo resultado
    """
    # verificar se simulacao existe
    simulation = crud.SimulationCRUD.get(db, result.simulation_id)
    if not simulation:
        raise HTTPException(
            status_code=404,
            detail=f"simulacao {result.simulation_id} nao encontrada"
        )
    if simulation.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail=f"simulacao {result.simulation_id} nao encontrada"
        )
    
    try:
        db_result = crud.ResultCRUD.create(db, result)
        return db_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao criar resultado: {str(e)}")


@router.post("/results/bulk", response_model=List[schemas.ResultResponse], tags=["database", "results"])
async def create_results_bulk(
    results: List[schemas.ResultCreate],
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    criar multiplos resultados em batch (para pos-processamento)
    """
    try:
        for r in results:
            sim = crud.SimulationCRUD.get(db, r.simulation_id)
            if not sim or sim.user_id != user_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"simulacao {r.simulation_id} nao encontrada",
                )
        db_results = crud.ResultCRUD.create_bulk(db, results)
        return db_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao criar resultados: {str(e)}")


@router.get("/results/simulation/{simulation_id}", response_model=schemas.ResultListResponse, tags=["database", "results"])
async def get_simulation_results(
    simulation_id: int,
    result_type: Optional[str] = Query(None, description="filtrar por tipo"),
    search: Optional[str] = Query(None, description="filtrar por nome"),
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(None, ge=1, le=100),
    per_page: Optional[int] = Query(None, ge=1, le=100, description="alias legado de limit"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    listar resultados de uma simulacao especifica
    """
    # verificar se simulacao existe
    simulation = crud.SimulationCRUD.get(db, simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    if simulation.user_id != user_id:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")

    page, limit, skip = resolve_page_limit(page=page, limit=limit, per_page=per_page)
    results, total = crud.ResultCRUD.list_filtered_by_simulation(
        db,
        simulation_id,
        result_type=result_type,
        search=search,
        skip=skip,
        limit=limit,
    )
    return schemas.ResultListResponse(
        **build_paginated_payload(
            items=results,
            total=total,
            page=page,
            limit=limit,
            applied_filters=clean_filters(
                simulation_id=simulation_id,
                result_type=result_type,
                search=search,
            ),
        )
    )


@router.get("/results/{result_id}", response_model=schemas.ResultResponse, tags=["database", "results"])
async def get_result(
    result_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    obter resultado especifico
    """
    db_result = crud.ResultCRUD.get(db, result_id)
    if not db_result:
        raise HTTPException(status_code=404, detail="resultado nao encontrado")
    sim = crud.SimulationCRUD.get(db, db_result.simulation_id)
    if not sim or sim.user_id != user_id:
        raise HTTPException(status_code=404, detail="resultado nao encontrado")
    return db_result


# ==================== ENDPOINTS DE INGESTAO E RESUMOS PARA DASHBOARD ====================

@router.post(
    "/simulations/{simulation_id}/ingest-results",
    response_model=schemas.SimulationResponse,
    tags=["database", "simulations"],
)
async def ingest_results_for_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    ler generated/cfd/NOME_CASO/results.json e atualizar Simulation/Result.

    este endpoint pode ser chamado apos a simulacao openfoam concluir.
    """
    sim = crud.SimulationCRUD.get(db, simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    if sim.user_id != user_id:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")

    try:
        updated = results_service.ingest_simulation_results(db, simulation_id)
        if not updated:
            raise HTTPException(status_code=404, detail="simulacao nao encontrada")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao ingerir resultados: {str(e)}")


@router.delete("/results/{result_id}", tags=["database", "results"])
async def delete_result(
    result_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    deletar resultado
    """
    db_result = crud.ResultCRUD.get(db, result_id)
    if not db_result:
        raise HTTPException(status_code=404, detail="resultado nao encontrado")
    sim = crud.SimulationCRUD.get(db, db_result.simulation_id)
    if not sim or sim.user_id != user_id:
        raise HTTPException(status_code=404, detail="resultado nao encontrado")
    success = crud.ResultCRUD.delete(db, result_id)
    if not success:
        raise HTTPException(status_code=404, detail="resultado nao encontrado")
    return {"message": "resultado deletado com sucesso", "result_id": result_id}


# ==================== ENDPOINTS COMPOSTOS ====================

@router.get("/beds/{bed_id}/simulations", response_model=schemas.SimulationListResponse, tags=["database", "beds"])
async def get_bed_simulations(
    bed_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    listar todas simulacoes de um leito especifico
    """
    # verificar se bed existe
    bed = crud.BedCRUD.get(db, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    if bed.user_id != user_id:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    
    skip, limit, _ = crud.paginate(0, page, per_page)
    simulations, total = crud.SimulationCRUD.get_by_bed(
        db, bed_id, skip, limit, user_id=user_id
    )
    
    import math
    pages = math.ceil(total / per_page) if total > 0 else 1
    
    return schemas.SimulationListResponse(
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        items=simulations
    )


@router.get("/beds/{bed_id}/summary", tags=["database", "beds"])
async def get_bed_summary(
    bed_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    obter resumo de um leito (com estatisticas de simulacoes)
    """
    bed = crud.BedCRUD.get(db, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    if bed.user_id != user_id:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    
    # contar simulacoes por status
    from sqlalchemy import func
    from backend.app.database.models import Simulation
    
    stats = db.query(
        Simulation.status,
        func.count(Simulation.id)
    ).filter(
        Simulation.bed_id == bed_id,
        Simulation.user_id == user_id,
    ).group_by(Simulation.status).all()
    
    status_counts = {status: count for status, count in stats}
    
    # calcular metricas medias das simulacoes completadas
    from sqlalchemy import func as sql_func
    avg_metrics = db.query(
        sql_func.avg(Simulation.pressure_drop).label('avg_pressure_drop'),
        sql_func.avg(Simulation.average_velocity).label('avg_velocity'),
        sql_func.avg(Simulation.reynolds_number).label('avg_reynolds'),
        sql_func.avg(Simulation.execution_time).label('avg_execution_time')
    ).filter(
        Simulation.bed_id == bed_id,
        Simulation.user_id == user_id,
        Simulation.status == 'completed'
    ).first()
    
    return {
        "bed": schemas.BedResponse.model_validate(bed),
        "simulations_count": sum(status_counts.values()),
        "simulations_by_status": status_counts,
        "average_metrics": {
            "pressure_drop": avg_metrics.avg_pressure_drop,
            "velocity": avg_metrics.avg_velocity,
            "reynolds_number": avg_metrics.avg_reynolds,
            "execution_time": avg_metrics.avg_execution_time
        }
    }


@router.get("/stats/overview", tags=["database", "stats"])
async def get_overview_stats(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    obter estatisticas gerais do sistema
    """
    from sqlalchemy import func
    from backend.app.database.models import Bed, Simulation, Result
    
    total_beds = (
        db.query(func.count(Bed.id)).filter(Bed.user_id == user_id).scalar()
    )
    total_simulations = (
        db.query(func.count(Simulation.id))
        .filter(Simulation.user_id == user_id)
        .scalar()
    )
    total_results = (
        db.query(func.count(Result.id))
        .join(Simulation, Result.simulation_id == Simulation.id)
        .filter(Simulation.user_id == user_id)
        .scalar()
    )
    
    # simulacoes por status
    sim_stats = db.query(
        Simulation.status,
        func.count(Simulation.id)
    ).filter(Simulation.user_id == user_id).group_by(Simulation.status).all()
    
    simulations_by_status = {status: count for status, count in sim_stats}
    
    # ultimas simulacoes
    recent_simulations = (
        db.query(Simulation)
        .filter(Simulation.user_id == user_id)
        .order_by(Simulation.created_at.desc())
        .limit(5)
        .all()
    )
    
    return {
        "total_beds": total_beds,
        "total_simulations": total_simulations,
        "total_results": total_results,
        "simulations_by_status": simulations_by_status,
        "recent_simulations": [schemas.SimulationResponse.model_validate(s) for s in recent_simulations]
    }


def _describe_database_url(url: str) -> tuple[str, str]:
    u = (url or "").lower()
    if "sqlite" in u:
        return "sqlite", "sqlite · ficheiro local"
    if "postgres" in u:
        return "postgresql", "postgresql · servidor"
    return "other", "motor sql (ver DATABASE_URL)"


def _dt_iso(v) -> str:
    if v is None:
        return ""
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return str(v)


@router.get(
    "/database/panel",
    response_model=DatabasePanelResponse,
    tags=["database", "admin"],
)
async def get_database_panel(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    dados agregados para a página "banco de dados" no frontend:
    motor sql (sem expor credenciais), contagens de tabelas e últimos eventos do painel.
    """
    backend, display = _describe_database_url(DATABASE_URL)
    now = datetime.now(timezone.utc).isoformat()
    integrations = {
        "redis": "não integrado à api",
        "object_storage": "não integrado à api",
    }

    try:
        beds = (
            db.query(func.count(models.Bed.id))
            .filter(models.Bed.user_id == user_id)
            .scalar()
            or 0
        )
        sims = (
            db.query(func.count(models.Simulation.id))
            .filter(models.Simulation.user_id == user_id)
            .scalar()
            or 0
        )
        res = (
            db.query(func.count(models.Result.id))
            .join(
                models.Simulation,
                models.Result.simulation_id == models.Simulation.id,
            )
            .filter(models.Simulation.user_id == user_id)
            .scalar()
            or 0
        )
        tmpl = (
            db.query(func.count(models.BedTemplate.id))
            .filter(models.BedTemplate.user_id == user_id)
            .scalar()
            or 0
        )

        ev_rows = (
            db.query(models.AdminPanelEvent)
            .order_by(models.AdminPanelEvent.created_at.desc())
            .limit(20)
            .all()
        )
        events = [
            DatabasePanelEventOut(
                id=e.id,
                event_type=e.event_type,
                detail=e.detail,
                created_at=_dt_iso(e.created_at),
            )
            for e in ev_rows
        ]

        return DatabasePanelResponse(
            connected=True,
            backend=backend,
            database_display=display,
            counts=DatabasePanelCounts(
                beds=beds,
                simulations=sims,
                results=res,
                bed_templates=tmpl,
            ),
            integrations=integrations,
            recent_events=events,
            checked_at=now,
            error=None,
        )
    except Exception as e:
        return DatabasePanelResponse(
            connected=False,
            backend=backend,
            database_display=display,
            counts=DatabasePanelCounts(
                beds=0,
                simulations=0,
                results=0,
                bed_templates=0,
            ),
            integrations=integrations,
            recent_events=[],
            checked_at=now,
            error=str(e),
        )


@router.post("/database/events", tags=["database", "admin"])
async def log_database_panel_event(
    body: AdminPanelEventCreate,
    db: Session = Depends(get_db),
):
    """
    regista um pedido do painel (backup manual ou teste de ligação) na tabela admin_panel_events.
    """
    row = models.AdminPanelEvent(
        event_type=body.event_type,
        detail=body.detail,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "event_type": row.event_type,
        "created_at": _dt_iso(row.created_at),
    }

