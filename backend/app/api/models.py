# tipos pydantic partilhados entre routers pedidos e respostas json
# enums string garantem valores estaveis no openapi e no frontend
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from enum import Enum
from datetime import datetime

# valores permitidos para campo status de Job
class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# categorias de trabalho em background
class JobType(str, Enum):
    COMPILE = "compile"
    GENERATE_MODEL = "generate_model"
    SIMULATION = "simulation"
    FULL_PIPELINE = "full_pipeline"

# corpo flat para endpoint compile sem nesting wizard
# field com ge le valida intervalos fisicos simples antes de tocar no disco
class BedParameters(BaseModel):
    # geometria do leito
    diameter: float = Field(..., description="diâmetro do leito (m)", ge=0.01, le=1.0)
    height: float = Field(..., description="altura do leito (m)", ge=0.01, le=2.0)
    wall_thickness: float = Field(0.002, description="espessura da parede (m)")
    
    # tampas
    lid_top: str = Field("flat", description="tipo tampa superior (flat/hemispherical/none)")
    lid_bottom: str = Field("flat", description="tipo tampa inferior")
    lid_thickness: float = Field(0.003, description="espessura das tampas (m)")
    
    # partículas
    particle_count: int = Field(..., description="quantidade de partículas", ge=10, le=10000)
    particle_type: str = Field("sphere", description="tipo de partícula (sphere/cube)")
    particle_diameter: float = Field(..., description="diâmetro da partícula (m)", ge=0.001, le=0.1)
    
    # empacotamento
    # estes campos alimentam bed service e depois o json usado pelo blender
    # rigid body mantem simulacao antiga
    # spherical packing e hexagonal 3d usam o pacote packed bed science no script leito extracao
    packing_method: str = Field(
        "rigid_body",
        description=(
            "método: rigid_body (física blender), spherical_packing ou hexagonal_3d "
            "(posições determinísticas no script leito_extracao)"
        ),
    )
    gravity: float = Field(-9.81, description="gravidade (m/s²)")
    friction: float = Field(0.5, description="coeficiente de atrito")
    substeps: int = Field(10, description="substeps da simulação física")
    packing_gap: float = Field(
        0.0,
        description="folga mínima entre superfícies das esferas (m); modos científicos",
    )
    packing_random_seed: Optional[int] = Field(
        None, description="seed opcional para spherical_packing"
    )
    max_placement_attempts: int = Field(
        500_000,
        description="tentativas máximas de colocação aleatória (spherical_packing)",
    )
    strict_validation: bool = Field(
        True,
        description="se true, falha no blender se validação geométrica ou contagem",
    )
    hex_step_x: Optional[float] = Field(
        None,
        description="passo opcional da grade hexagonal (m); padrão 2*r+gap",
    )
    
    # cfd (opcional)
    cfd_regime: Optional[str] = Field("laminar", description="regime do fluido")
    inlet_velocity: Optional[float] = Field(0.01, description="velocidade entrada (m/s)")
    fluid_density: Optional[float] = Field(1000.0, description="densidade fluido (kg/m³)")
    fluid_viscosity: Optional[float] = Field(0.001, description="viscosidade (Pa.s)")

# modelo para estrutura aninhada do frontend
class BedParametersNested(BaseModel):
    """parâmetros do leito empacotado em estrutura aninhada (frontend)"""
    bed: Dict[str, Any] = Field(..., description="parâmetros do leito")
    lids: Dict[str, Any] = Field(..., description="parâmetros das tampas")
    particles: Dict[str, Any] = Field(..., description="parâmetros das partículas")
    packing: Dict[str, Any] = Field(..., description="parâmetros do empacotamento")
    export: Dict[str, Any] = Field(..., description="parâmetros de exportação")
    cfd: Optional[Dict[str, Any]] = Field(None, description="parâmetros CFD (opcional)")
    geometry_mode: Optional[str] = Field(None, description="full_3d, pseudo_2d_thin_slice, pseudo_2d_statistical")
    generation_backend: Optional[str] = Field(None, description="python_engine ou blender")
    slice: Optional[Dict[str, Any]] = Field(None, description="parametros thin slice")
    statistical_2d: Optional[Dict[str, Any]] = Field(None, description="parametros rsa 2d")
    packing_mode: Optional[str] = Field(None, description="alias de packing.method na raiz")

class CompileRequest(BaseModel):
    """requisição para compilar arquivo .bed"""
    parameters: BedParameters
    filename: Optional[str] = Field(None, description="nome do arquivo (auto se null)")

class CompileResponse(BaseModel):
    """resposta da compilação"""
    success: bool
    bed_file: str
    json_file: str
    message: str

class GenerateModelRequest(BaseModel):
    """requisição para gerar modelo 3d"""
    json_file: str
    open_blender: bool = Field(False, description="abrir blender gui após gerar")
    modeling_profile: Optional[str] = Field(
        None,
        description=(
            "motor de geometria: blender ou blender_python (blend), "
            "python ou pure_python (stl via packed_bed_stl); None usa env MODELING_PROFILE"
        ),
    )

class SimulationRequest(BaseModel):
    """requisição para criar simulação cfd"""
    json_file: str
    blend_file: str
    run_simulation: bool = Field(False, description="executar simulação imediatamente")
    modeling_profile: Optional[str] = Field(
        None,
        description="informativo; mesmo conjunto de aliases que em gerar modelo",
    )

# modelos de job (tarefa assíncrona)
# progress inteiro 0 a 100 para barras na ui
class Job(BaseModel):
    """tarefa assíncrona"""
    job_id: str
    job_type: JobType
    status: JobStatus
    progress: int = Field(0, ge=0, le=100)
    created_at: datetime
    updated_at: datetime
    output_files: List[str] = []
    logs: List[str] = []
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}

class JobResponse(BaseModel):
    """resposta de criação de job"""
    job_id: str
    status: JobStatus
    message: str

# modelos de listagem
class FileInfo(BaseModel):
    """informações de arquivo"""
    filename: str
    path: str
    size: int
    created_at: datetime

# modelos para templates
class TemplateCreate(BaseModel):
    """criar template"""
    name: str = Field(..., description="nome do template")
    content: str = Field(..., description="conteúdo do template")
    tag: str = Field(default="bed", description="etiqueta: bed, preset, cfd, …")
    source: str = Field(default="editor", description="origem: editor, import, duplicate")


class TemplateSummary(BaseModel):
    """listagem de templates sem conteúdo (payload leve)"""
    id: str
    name: str
    created_at: str
    updated_at: str
    tag: str = "bed"
    source: str = "editor"


class PaginatedTemplateSummary(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
    per_page: int
    pages: int
    items: List[TemplateSummary]


class TemplateResponse(BaseModel):
    """resposta de template com conteúdo completo"""
    id: str
    name: str
    content: str
    created_at: str
    updated_at: str
    tag: str = "bed"
    source: str = "editor"


class Template(BaseModel):
    """template completo (legado / alias semântico)"""
    id: str
    name: str
    content: str
    created_at: str
    updated_at: str
    tag: str = "bed"
    source: str = "editor"

class FileListResponse(BaseModel):
    """lista de arquivos"""
    files: List[FileInfo]
    total: int


# painel banco de dados (frontend)
class DatabasePanelCounts(BaseModel):
    beds: int
    simulations: int
    results: int
    bed_templates: int


class DatabasePanelEventOut(BaseModel):
    id: int
    event_type: str
    detail: Optional[str] = None
    created_at: str


class DatabasePanelResponse(BaseModel):
    connected: bool
    backend: str
    database_display: str
    counts: DatabasePanelCounts
    integrations: Dict[str, str] = Field(default_factory=dict)
    recent_events: List[DatabasePanelEventOut] = Field(default_factory=list)
    checked_at: str
    error: Optional[str] = None


class AdminPanelEventCreate(BaseModel):
    event_type: Literal["backup_request", "connection_test"]
    detail: Optional[str] = Field(None, max_length=2000)


# relatórios (página web)
class ReportCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    body: str = ""
    status: Literal["draft", "planned", "published"] = "draft"


class ReportUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    body: Optional[str] = None
    status: Optional[Literal["draft", "planned", "published"]] = None


class ReportSummary(BaseModel):
    id: int
    title: str
    status: str
    created_at: str
    updated_at: str
    attachment_count: int


class PaginatedReportSummary(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
    per_page: int
    pages: int
    items: List[ReportSummary]


class ReportAttachmentOut(BaseModel):
    id: int
    kind: str
    ref_id: Optional[str] = None
    label: Optional[str] = None
    note: Optional[str] = None
    created_at: str
    display_ref: str


class ReportDetail(BaseModel):
    id: int
    title: str
    body: str
    status: str
    created_at: str
    updated_at: str
    attachments: List[ReportAttachmentOut]


class ReportAttachmentCreate(BaseModel):
    kind: Literal["simulation", "template", "result", "data_note"]
    ref_id: Optional[str] = Field(None, max_length=64)
    label: Optional[str] = Field(None, max_length=500)
    note: Optional[str] = None


class ReportCatalogSimulation(BaseModel):
    id: int
    name: str
    status: str


class ReportCatalogTemplate(BaseModel):
    id: str
    name: str
    tag: str = "bed"


class ReportCatalogResponse(BaseModel):
    simulations: List[ReportCatalogSimulation]
    templates: List[ReportCatalogTemplate]


class ReportMetaResultItem(BaseModel):
    id: int
    name: str
    result_type: str
    value: Optional[float] = None
    unit: Optional[str] = None


# perfil (singleton na base de dados)
class UserProfileResponse(BaseModel):
    id: int
    display_name: str
    email: str
    organization: str
    role: str
    bio: Optional[str] = None
    preferred_language: str
    created_at: str
    updated_at: str


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    organization: Optional[str] = Field(None, max_length=300)
    role: Optional[Literal["researcher", "engineer", "student", "other"]] = None
    bio: Optional[str] = None
    preferred_language: Optional[Literal["pt", "en"]] = None


class DatabaseUiOptions(BaseModel):
    notes: str = ""
    client_timeout_sec: int = Field(30, ge=5, le=600)


class OpenFoamDefaults(BaseModel):
    solver: str = "simpleFoam"
    max_iterations: int = Field(1000, ge=1, le=100000)
    turbulence_model: str = "kEpsilon"
    convergence: float = Field(1e-6, gt=0)


class ModelingOptions(BaseModel):
    profile: Literal["blender", "python"] = "blender"
    notes: str = ""


class CfdOtherNotes(BaseModel):
    notes: str = ""


class AppSettingsResponse(BaseModel):
    id: int
    theme_mode: str
    language: str
    jobs_poll_interval_sec: int
    show_advanced_hints: bool
    simple_mode: bool = False
    dev_mode: bool = False
    database_ui: DatabaseUiOptions
    openfoam_defaults: OpenFoamDefaults
    modeling: ModelingOptions
    cfd_other: CfdOtherNotes
    created_at: str
    updated_at: str


class AppSettingsUpdate(BaseModel):
    theme_mode: Optional[Literal["light", "dark", "system"]] = None
    language: Optional[Literal["pt", "en"]] = None
    jobs_poll_interval_sec: Optional[int] = Field(None, ge=3, le=120)
    show_advanced_hints: Optional[bool] = None
    simple_mode: Optional[bool] = None
    dev_mode: Optional[bool] = None
    database_ui: Optional[DatabaseUiOptions] = None
    openfoam_defaults: Optional[OpenFoamDefaults] = None
    modeling: Optional[ModelingOptions] = None
    cfd_other: Optional[CfdOtherNotes] = None

