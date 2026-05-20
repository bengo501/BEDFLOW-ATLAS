# schemas pydantic espelham colunas sql para entrada e saida http segura
# validators extras impedem strings livres em campos enumerados simples
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


# schemas para Bed

class BedBase(BaseModel):
    """schema base para leito"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    diameter: float = Field(..., gt=0, le=1.0, description="diametro em metros")
    height: float = Field(..., gt=0, le=2.0, description="altura em metros")
    wall_thickness: float = Field(..., gt=0, le=0.1, description="espessura em metros")
    particle_count: int = Field(..., ge=10, le=10000, description="numero de particulas")
    particle_diameter: float = Field(..., gt=0, le=0.1, description="diametro particula em metros")
    particle_kind: str = Field(..., description="tipo de particula")
    packing_method: str = Field(..., description="metodo de empacotamento")
    porosity: Optional[float] = Field(None, ge=0, le=1, description="porosidade")


class BedCreate(BedBase):
    """schema para criar leito"""
    parameters_json: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    # caminhos opcionais usados quando o leito e gerado pela api compile
    bed_file_path: Optional[str] = None
    json_file_path: Optional[str] = None
    blend_file_path: Optional[str] = None
    stl_file_path: Optional[str] = None


class BedUpdate(BaseModel):
    """schema para atualizar leito"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    porosity: Optional[float] = Field(None, ge=0, le=1)
    bed_file_path: Optional[str] = None
    json_file_path: Optional[str] = None
    blend_file_path: Optional[str] = None
    stl_file_path: Optional[str] = None
    parameters_json: Optional[Dict[str, Any]] = None


class BedResponse(BedBase):
    """schema de resposta para leito"""
    id: int
    user_id: int = 1
    bed_file_path: Optional[str]
    json_file_path: Optional[str]
    blend_file_path: Optional[str]
    stl_file_path: Optional[str]
    parameters_json: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


# schemas para Simulation

class SimulationBase(BaseModel):
    """schema base para simulacao"""
    bed_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    regime: str = Field(..., description="laminar ou turbulent")
    inlet_velocity: float = Field(..., gt=0, le=100, description="velocidade em m/s")
    fluid_density: float = Field(..., gt=0, description="densidade em kg/m³")
    fluid_viscosity: float = Field(..., gt=0, description="viscosidade em Pa·s")
    solver: str = Field(default="simpleFoam")
    max_iterations: int = Field(default=1000, ge=100, le=100000)
    convergence_criteria: float = Field(default=1e-4, gt=0, le=1)
    
    @validator('regime')
    def validate_regime(cls, v):
        if v not in ['laminar', 'turbulent']:
            raise ValueError('regime deve ser laminar ou turbulent')
        return v


class SimulationCreate(SimulationBase):
    """schema para criar simulacao"""
    parameters_json: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class SimulationUpdate(BaseModel):
    """schema para atualizar simulacao"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, description="pending, running, completed, failed")
    progress: Optional[int] = Field(None, ge=0, le=100)
    mesh_cells_count: Optional[int] = None
    mesh_quality: Optional[str] = None
    case_directory: Optional[str] = None
    log_file_path: Optional[str] = None
    pressure_drop: Optional[float] = None
    average_velocity: Optional[float] = None
    reynolds_number: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['pending', 'running', 'completed', 'failed']:
            raise ValueError('status invalido')
        return v


class SimulationDetailResponse(BaseModel):
    """leitura por id — sem validadores estritos de SimulationBase (dados legados na bd)"""
    id: int
    user_id: int = 1
    bed_id: int
    name: str
    description: Optional[str] = None
    regime: str
    inlet_velocity: float
    fluid_density: float
    fluid_viscosity: float
    solver: str = "simpleFoam"
    max_iterations: int = 1000
    convergence_criteria: float = 1e-4
    status: str
    progress: Optional[int] = 0
    mesh_cells_count: Optional[int] = None
    mesh_quality: Optional[str] = None
    case_directory: Optional[str] = None
    log_file_path: Optional[str] = None
    pressure_drop: Optional[float] = None
    average_velocity: Optional[float] = None
    reynolds_number: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    parameters_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class SimulationResponse(SimulationBase):
    """schema de resposta para simulacao"""
    id: int
    user_id: int = 1
    status: str
    progress: int
    mesh_cells_count: Optional[int]
    mesh_quality: Optional[str]
    case_directory: Optional[str]
    log_file_path: Optional[str]
    pressure_drop: Optional[float]
    average_velocity: Optional[float]
    reynolds_number: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time: Optional[float]
    parameters_json: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class Model3DResponse(BaseModel):
    """representa um modelo 3d persistido a partir de um leito"""
    id: int
    user_id: int = 1
    name: str
    description: Optional[str] = None
    diameter: float
    height: float
    wall_thickness: float
    particle_count: int
    particle_diameter: float
    particle_kind: str
    packing_method: str
    porosity: Optional[float] = None
    geometry_mode: Optional[str] = None
    generation_backend: Optional[str] = None
    porosity_target: Optional[float] = None
    porosity_result: Optional[float] = None
    slice_axis: Optional[str] = None
    slice_thickness: Optional[float] = None
    internal_cylinder_mode: Optional[str] = None
    boolean_operation_status: Optional[Dict[str, Any]] = None
    boolean_outer_shell: Optional[str] = None
    boolean_inner_core: Optional[str] = None
    boolean_particle_tools: Optional[str] = None
    boolean_backend: Optional[str] = None
    boolean_warnings: Optional[str] = None
    bed_file_path: Optional[str] = None
    json_file_path: Optional[str] = None
    blend_file_path: Optional[str] = None
    stl_file_path: Optional[str] = None
    blend_file_url: Optional[str] = None
    stl_file_url: Optional[str] = None
    preview_model_url: Optional[str] = None
    has_model_files: bool = False
    parameters_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None


class Model3DListResponse(BaseModel):
    """lista paginada de modelos 3d persistidos"""
    total: int
    page: int
    limit: int
    total_pages: int
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
    per_page: int
    pages: int
    items: List[Model3DResponse]


class HistoryEntryResponse(BaseModel):
    """evento agregado para a pagina de historico"""
    entry_type: str
    source_id: int
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    simulation_id: Optional[int] = None
    model_3d_id: Optional[int] = None
    bed_id: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HistoryResponse(BaseModel):
    """feed agregado usado pelo historico"""
    total: int = 0
    page: int = 1
    limit: int = 100
    total_pages: int = 1
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
    per_page: int = 100
    pages: int = 1
    simulations: List[SimulationResponse]
    models_3d: List[Model3DResponse]
    items: List[HistoryEntryResponse]


class DashboardSummaryResponse(BaseModel):
    """resumo consolidado para dashboard"""
    total_simulations: int
    total_models_3d: int
    by_status: Dict[str, int]
    success_rate: float
    average_execution_time: Optional[float] = None
    average_pressure_drop: Optional[float] = None
    average_reynolds_number: Optional[float] = None
    recent_simulations: List[SimulationResponse]
    recent_models_3d: List[Model3DResponse]


class ArtifactDirBreakdown(BaseModel):
    label: str
    path: str
    size_bytes: int


class ArtifactsStorageResponse(BaseModel):
    """uso em disco dos artefactos vs teto (60 gib) para o dashboard"""
    bytes_used: int
    bytes_cap: int
    cap_gb: float
    percent_of_cap: float
    breakdown: List[ArtifactDirBreakdown]

class ResultBase(BaseModel):
    """schema base para resultado"""
    simulation_id: int = Field(..., gt=0)
    result_type: str = Field(..., description="field, metric, validation, visualization")
    name: str = Field(..., min_length=1, max_length=255)
    value: Optional[float] = None
    unit: Optional[str] = Field(None, max_length=50)
    data_json: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    timestep: Optional[int] = None
    
    @validator('result_type')
    def validate_result_type(cls, v):
        valid_types = ['field', 'metric', 'validation', 'visualization']
        if v not in valid_types:
            raise ValueError(f'result_type deve ser um de: {valid_types}')
        return v


class ResultCreate(ResultBase):
    """schema para criar resultado"""
    pass


class ResultResponse(ResultBase):
    """schema de resposta para resultado"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# schemas de listagem com paginacao

class PaginatedResponse(BaseModel):
    """schema para resposta paginada"""
    total: int = Field(..., description="total de items")
    page: int = Field(..., ge=1, description="pagina atual")
    per_page: int = Field(..., ge=1, le=100, description="items por pagina")
    pages: int = Field(..., description="total de paginas")
    items: List[Any] = Field(..., description="items da pagina")


class BedListResponse(BaseModel):
    """schema de resposta para lista de leitos"""
    total: int
    page: int
    limit: int
    total_pages: int
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
    per_page: int
    pages: int
    items: List[BedResponse]


class SimulationListResponse(BaseModel):
    """schema de resposta para lista de simulacoes"""
    total: int
    page: int
    limit: int
    total_pages: int
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
    per_page: int
    pages: int
    items: List[SimulationResponse]


class ResultListResponse(BaseModel):
    """schema de resposta para lista de resultados"""
    total: int
    page: int
    limit: int
    total_pages: int
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
    per_page: int
    pages: int
    items: List[ResultResponse]

