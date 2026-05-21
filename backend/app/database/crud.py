# funcoes que traduzem operacoes http em comandos sqlalchemy
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from . import models, schemas
import math


class BedCRUD:
    # crud para tabela beds
    @staticmethod
    def create(db: Session, bed: schemas.BedCreate, user_id: int = 1) -> models.Bed:
        # converte o schema pydantic em dict compativel com o modelo sqlalchemy
        # injeta user id depois do dump para o cliente nunca fingir outro dono
        data = bed.model_dump() if hasattr(bed, "model_dump") else bed.dict()
        data["user_id"] = user_id
        db_bed = models.Bed(**data)
        db.add(db_bed)
        db.commit()
        db.refresh(db_bed)
        return db_bed

    @staticmethod
    def get(db: Session, bed_id: int) -> Optional[models.Bed]:
        # procura pk exacta devolve primeira linha ou None
        return db.query(models.Bed).filter(models.Bed.id == bed_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[models.Bed]:
        # unico por nome na logica da api antes de criar duplicado
        return db.query(models.Bed).filter(models.Bed.name == name).first()

    @staticmethod
    def get_by_name_for_user(
        db: Session, name: str, user_id: int
    ) -> Optional[models.Bed]:
        # o mesmo nome pode existir para outro utilizador
        # por isso o filtro inclui sempre user id
        return (
            db.query(models.Bed)
            .filter(models.Bed.name == name, models.Bed.user_id == user_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
    ) -> Tuple[List[models.Bed], int]:
        # conta total para paginas depois aplica offset e limit
        # comeca com select geral sobre beds
        query = db.query(models.Bed)
        # se user id vier preenchido restringe ao dono
        if user_id is not None:
            query = query.filter(models.Bed.user_id == user_id)
        total = query.count()
        beds = query.order_by(models.Bed.created_at.desc()).offset(skip).limit(limit).all()
        return beds, total

    @staticmethod
    def update(
        db: Session,
        bed_id: int,
        bed_update: schemas.BedUpdate
    ) -> Optional[models.Bed]:
        # so escreve campos que vieram no patch exclude_unset True
        db_bed = db.query(models.Bed).filter(models.Bed.id == bed_id).first()
        if not db_bed:
            return None

        update_data = bed_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_bed, field, value)

        db.commit()
        db.refresh(db_bed)
        return db_bed

    @staticmethod
    def delete(db: Session, bed_id: int) -> bool:
        # apaga linha devolve False se nao existia
        db_bed = db.query(models.Bed).filter(models.Bed.id == bed_id).first()
        if not db_bed:
            return False

        db.delete(db_bed)
        db.commit()
        return True

    @staticmethod
    def search(
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
    ) -> Tuple[List[models.Bed], int]:
        # ilike com wildcards nos dois lados para nome ou descricao
        search_query = db.query(models.Bed).filter(
            (models.Bed.name.ilike(f"%{query}%")) |
            (models.Bed.description.ilike(f"%{query}%"))
        )
        if user_id is not None:
            search_query = search_query.filter(models.Bed.user_id == user_id)
        total = search_query.count()
        beds = search_query.order_by(models.Bed.created_at.desc()).offset(skip).limit(limit).all()
        return beds, total

    @staticmethod
    def list_filtered(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        search: Optional[str] = None,
        packing_method: Optional[str] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
    ) -> Tuple[List[models.Bed], int]:
        query = db.query(models.Bed)
        if user_id is not None:
            query = query.filter(models.Bed.user_id == user_id)
        if search:
            like = f"%{search.strip()}%"
            query = query.filter(
                (models.Bed.name.ilike(like)) | (models.Bed.description.ilike(like))
            )
        if packing_method:
            query = query.filter(models.Bed.packing_method == packing_method)
        if created_from:
            query = query.filter(models.Bed.created_at >= created_from)
        if created_to:
            query = query.filter(models.Bed.created_at <= created_to)
        total = query.count()
        beds = (
            query.order_by(models.Bed.updated_at.desc(), models.Bed.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return beds, total


class SimulationCRUD:
    # crud para tabela simulations
    @staticmethod
    def create(
        db: Session,
        simulation: schemas.SimulationCreate,
        user_id: int = 1,
        **extra_fields,
    ) -> models.Simulation:
        # extra fields permite preencher colunas que nao estao no schema minimo
        # por exemplo status inicial e pasta do caso openfoam criado por servicos
        data = (
            simulation.model_dump()
            if hasattr(simulation, "model_dump")
            else simulation.dict()
        )
        data["user_id"] = user_id
        data.update(extra_fields)
        db_simulation = models.Simulation(**data)
        db.add(db_simulation)
        db.commit()
        db.refresh(db_simulation)
        return db_simulation

    @staticmethod
    def get(db: Session, simulation_id: int) -> Optional[models.Simulation]:
        return db.query(models.Simulation).filter(
            models.Simulation.id == simulation_id
        ).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
    ) -> Tuple[List[models.Simulation], int]:
        query = db.query(models.Simulation)
        if user_id is not None:
            query = query.filter(models.Simulation.user_id == user_id)
        total = query.count()
        simulations = query.order_by(
            models.Simulation.created_at.desc()
        ).offset(skip).limit(limit).all()
        return simulations, total

    @staticmethod
    def get_by_bed(
        db: Session,
        bed_id: int,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
    ) -> Tuple[List[models.Simulation], int]:
        # filtra fk bed_id mantem ordenacao por data
        query = db.query(models.Simulation).filter(models.Simulation.bed_id == bed_id)
        if user_id is not None:
            query = query.filter(models.Simulation.user_id == user_id)
        total = query.count()
        simulations = query.order_by(
            models.Simulation.created_at.desc()
        ).offset(skip).limit(limit).all()
        return simulations, total

    @staticmethod
    def get_by_status(
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
    ) -> Tuple[List[models.Simulation], int]:
        query = db.query(models.Simulation).filter(models.Simulation.status == status)
        if user_id is not None:
            query = query.filter(models.Simulation.user_id == user_id)
        total = query.count()
        simulations = query.order_by(
            models.Simulation.created_at.desc()
        ).offset(skip).limit(limit).all()
        return simulations, total

    @staticmethod
    def list_filtered(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        bed_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        regime: Optional[str] = None,
        solver: Optional[str] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
    ) -> Tuple[List[models.Simulation], int]:
        query = db.query(models.Simulation)
        if user_id is not None:
            query = query.filter(models.Simulation.user_id == user_id)
        if bed_id is not None:
            query = query.filter(models.Simulation.bed_id == bed_id)
        if status:
            query = query.filter(models.Simulation.status == status)
        if regime:
            query = query.filter(models.Simulation.regime == regime)
        if solver:
            query = query.filter(models.Simulation.solver == solver)
        if search:
            like = f"%{search.strip()}%"
            query = query.filter(
                (models.Simulation.name.ilike(like))
                | (models.Simulation.description.ilike(like))
            )
        if created_from:
            query = query.filter(models.Simulation.created_at >= created_from)
        if created_to:
            query = query.filter(models.Simulation.created_at <= created_to)
        total = query.count()
        simulations = (
            query.order_by(models.Simulation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return simulations, total

    @staticmethod
    def update(
        db: Session,
        simulation_id: int,
        simulation_update: schemas.SimulationUpdate
    ) -> Optional[models.Simulation]:
        db_simulation = db.query(models.Simulation).filter(
            models.Simulation.id == simulation_id
        ).first()
        if not db_simulation:
            return None

        update_data = simulation_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_simulation, field, value)

        db.commit()
        db.refresh(db_simulation)
        return db_simulation

    @staticmethod
    def delete(db: Session, simulation_id: int) -> bool:
        db_simulation = db.query(models.Simulation).filter(
            models.Simulation.id == simulation_id
        ).first()
        if not db_simulation:
            return False

        db.delete(db_simulation)
        db.commit()
        return True


class ResultCRUD:
    # crud para tabela results
    @staticmethod
    def create(db: Session, result: schemas.ResultCreate) -> models.Result:
        db_result = models.Result(**result.dict())
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result

    @staticmethod
    def create_bulk(
        db: Session,
        results: List[schemas.ResultCreate]
    ) -> List[models.Result]:
        # uma transaccao para muitas linhas
        db_results = [models.Result(**result.dict()) for result in results]
        db.add_all(db_results)
        db.commit()
        for result in db_results:
            db.refresh(result)
        return db_results

    @staticmethod
    def get(db: Session, result_id: int) -> Optional[models.Result]:
        return db.query(models.Result).filter(models.Result.id == result_id).first()

    @staticmethod
    def get_by_simulation(
        db: Session,
        simulation_id: int,
        result_type: Optional[str] = None
    ) -> List[models.Result]:
        query = db.query(models.Result).filter(
            models.Result.simulation_id == simulation_id
        )
        if result_type:
            query = query.filter(models.Result.result_type == result_type)
        return query.order_by(models.Result.created_at.desc()).all()

    @staticmethod
    def list_filtered_by_simulation(
        db: Session,
        simulation_id: int,
        *,
        result_type: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[models.Result], int]:
        query = db.query(models.Result).filter(
            models.Result.simulation_id == simulation_id
        )
        if result_type:
            query = query.filter(models.Result.result_type == result_type)
        if search:
            like = f"%{search.strip()}%"
            query = query.filter(models.Result.name.ilike(like))
        total = query.count()
        results = (
            query.order_by(models.Result.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return results, total

    @staticmethod
    def delete(db: Session, result_id: int) -> bool:
        db_result = db.query(models.Result).filter(models.Result.id == result_id).first()
        if not db_result:
            return False

        db.delete(db_result)
        db.commit()
        return True

    @staticmethod
    def delete_by_simulation(db: Session, simulation_id: int) -> int:
        # devolve quantas linhas apagou
        deleted = db.query(models.Result).filter(
            models.Result.simulation_id == simulation_id
        ).delete()
        db.commit()
        return deleted


class JobCRUD:
    @staticmethod
    def upsert(db: Session, job) -> models.JobRecord:
        from backend.app.api.models import Job as ApiJob

        data = job
        if not isinstance(data, ApiJob):
            raise TypeError("job deve ser backend.app.api.models.Job")
        row = db.query(models.JobRecord).filter(
            models.JobRecord.job_id == data.job_id
        ).first()
        meta = dict(data.metadata or {})
        outputs = list(data.output_files or [])
        logs = list(data.logs or [])
        payload = {
            "job_type": str(data.job_type.value if hasattr(data.job_type, "value") else data.job_type),
            "status": str(data.status.value if hasattr(data.status, "value") else data.status),
            "progress": int(data.progress or 0),
            "metadata_json": meta,
            "output_files_json": outputs,
            "logs_json": logs,
            "error_message": data.error_message,
            "updated_at": data.updated_at,
        }
        if str(payload["status"]) in ("completed", "failed"):
            payload["completed_at"] = data.updated_at
        if row is None:
            row = models.JobRecord(job_id=data.job_id, created_at=data.created_at, **payload)
            db.add(row)
        else:
            for k, v in payload.items():
                setattr(row, k, v)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def get(db: Session, job_id: str) -> Optional[models.JobRecord]:
        return db.query(models.JobRecord).filter(
            models.JobRecord.job_id == job_id
        ).first()

    @staticmethod
    def list_all(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 500,
    ) -> List[models.JobRecord]:
        return (
            db.query(models.JobRecord)
            .order_by(models.JobRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def mark_stale_running_as_failed(db: Session) -> int:
        from backend.app.api.models import JobStatus

        rows = (
            db.query(models.JobRecord)
            .filter(
                models.JobRecord.status.in_(
                    [JobStatus.QUEUED.value, JobStatus.RUNNING.value]
                )
            )
            .all()
        )
        n = 0
        for row in rows:
            row.status = JobStatus.FAILED.value
            row.error_message = row.error_message or "interrompido (reinício do servidor)"
            row.updated_at = datetime.utcnow()
            n += 1
        if n:
            db.commit()
        return n


def paginate(
    total: int,
    page: int = 1,
    per_page: int = 50
) -> Tuple[int, int, int]:
    # converte numero de pagina em skip e limit para sql
    # pages e o total de paginas para mostrar no cliente
    page = max(1, page)
    per_page = min(per_page, 100)  # max 100 items por pagina

    skip = (page - 1) * per_page
    limit = per_page
    pages = math.ceil(total / per_page) if total > 0 else 1

    return skip, limit, pages
