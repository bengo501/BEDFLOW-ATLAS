# classes sqlalchemy uma tabela por classe
# relacionamentos usam cascade para apagar filhos quando apaga pai
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


# leito empacotado geometria particulas e caminhos de ficheiros gerados
class Bed(Base):
    __tablename__ = "beds"

    # chave surrogate e nome unico logico
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # dimensoes fisicas em metros
    diameter = Column(Float, nullable=False)  # metros
    height = Column(Float, nullable=False)    # metros
    wall_thickness = Column(Float, nullable=False)  # metros

    # quantidade e tipo de particulas
    particle_count = Column(Integer, nullable=False)
    particle_diameter = Column(Float, nullable=False)  # metros
    particle_kind = Column(String(50), nullable=False)  # sphere cylinder etc

    # como se empacotou e porosidade estimada
    packing_method = Column(String(50), nullable=False)  # rigid_body random etc
    porosity = Column(Float, nullable=True)  # fraccao vazia

    # caminhos relativos aos artefactos no disco
    bed_file_path = Column(String(500), nullable=True)      # caminho bed
    json_file_path = Column(String(500), nullable=True)     # caminho bed json
    blend_file_path = Column(String(500), nullable=True)    # caminho blend
    stl_file_path = Column(String(500), nullable=True)      # caminho stl

    # copia completa dos parametros de entrada em json
    parameters_json = Column(JSON, nullable=True)

    # auditoria quem criou e quando
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)  # origem api ou utilizador

    # isolamento por utilizador local (cabecalho x-user-id)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, default=1, index=True)

    # apagar leito apaga simulacoes filhas em cascade
    simulations = relationship("Simulation", back_populates="bed", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bed(id={self.id}, name='{self.name}', diameter={self.diameter}m, height={self.height}m)>"


# uma corrida cfd ligada a um leito com estado e metricas agregadas
class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    # fk obrigatoria para beds
    bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # propriedades do fluido e regime
    regime = Column(String(50), nullable=False)  # laminar turbulent
    inlet_velocity = Column(Float, nullable=False)  # m s
    fluid_density = Column(Float, nullable=False)   # kg m3
    fluid_viscosity = Column(Float, nullable=False) # Pa s

    # qualidade e tamanho da malha
    mesh_cells_count = Column(Integer, nullable=True)
    mesh_quality = Column(String(50), nullable=True)  # good acceptable poor

    # controlo numerico do solver openfoam
    solver = Column(String(50), nullable=False, default="simpleFoam")
    max_iterations = Column(Integer, nullable=False, default=1000)
    convergence_criteria = Column(Float, nullable=False, default=1e-4)

    # maquina de estados da corrida
    status = Column(String(50), nullable=False, default="pending")
    # pending running completed failed

    progress = Column(Integer, default=0)  # zero a cem por cento

    # pasta do caso e log principal
    case_directory = Column(String(500), nullable=True)
    log_file_path = Column(String(500), nullable=True)

    # escalares resumo pos processamento
    pressure_drop = Column(Float, nullable=True)  # Pa
    average_velocity = Column(Float, nullable=True)  # m s
    reynolds_number = Column(Float, nullable=True)

    # tempos reais de execucao
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time = Column(Float, nullable=True)  # segundos

    parameters_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)

    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, default=1, index=True)

    bed = relationship("Bed", back_populates="simulations")
    results = relationship("Result", back_populates="simulation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Simulation(id={self.id}, name='{self.name}', status='{self.status}')>"


# jobs assíncronos (geração de modelo, simulação, pipeline) — persistência permanente
class JobRecord(Base):
    __tablename__ = "jobs"

    job_id = Column(String(36), primary_key=True, index=True)
    job_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="queued", index=True)
    progress = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    output_files_json = Column(JSON, nullable=True)
    logs_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<JobRecord(job_id='{self.job_id}', type='{self.job_type}', status='{self.status}')>"


# linha de detalhe metrica campo ou ficheiro associado a uma simulacao
class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False, index=True)

    result_type = Column(String(50), nullable=False, index=True)
    # field metric validation visualization

    name = Column(String(255), nullable=False)

    value = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)

    data_json = Column(JSON, nullable=True)

    file_path = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=True)  # vtk csv png etc

    timestep = Column(Integer, nullable=True)  # passo temporal se aplicavel
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    simulation = relationship("Simulation", back_populates="results")

    def __repr__(self):
        return f"<Result(id={self.id}, type='{self.result_type}', name='{self.name}')>"


# texto bed guardado na base para reuso no editor
class BedTemplate(Base):
    __tablename__ = "bed_templates"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    tag = Column(String(50), nullable=False, default="bed")
    source = Column(String(50), nullable=False, default="editor")

    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, default=1, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<BedTemplate(id={self.id}, name='{self.name}')>"


# registo de accoes feitas na pagina administrativa da base
class AdminPanelEvent(Base):
    __tablename__ = "admin_panel_events"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AdminPanelEvent(id={self.id}, type='{self.event_type}')>"


# relatorio de utilizador com titulo corpo e estado editorial
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=False, default="")
    status = Column(String(32), nullable=False, default="draft")

    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, default=1, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    attachments = relationship(
        "ReportAttachment",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="ReportAttachment.id",
    )

    def __repr__(self):
        return f"<Report(id={self.id}, title='{self.title[:40]}...')>"


# ligacao fraca por strings ref_id a simulacao template resultado ou nota
class ReportAttachment(Base):
    __tablename__ = "report_attachments"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    report_id = Column(
        Integer,
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind = Column(String(32), nullable=False)
    ref_id = Column(String(64), nullable=True)
    label = Column(String(500), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    report = relationship("Report", back_populates="attachments")

    def __repr__(self):
        return f"<ReportAttachment(id={self.id}, kind='{self.kind}')>"


# uma linha de perfil local sem sistema de login multi conta
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    display_name = Column(String(200), nullable=False, default="")
    email = Column(String(255), nullable=False, default="")
    organization = Column(String(300), nullable=False, default="")
    role = Column(String(64), nullable=False, default="researcher")
    bio = Column(Text, nullable=True)
    preferred_language = Column(String(8), nullable=False, default="pt")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserProfile(id={self.id}, name='{self.display_name[:30]}')>"


# preferencias globais da ui e json extra options_json
class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True)
    theme_mode = Column(String(16), nullable=False, default="system")
    language = Column(String(8), nullable=False, default="pt")
    jobs_poll_interval_sec = Column(Integer, nullable=False, default=5)
    show_advanced_hints = Column(Boolean, nullable=False, default=False)
    options_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AppSettings(theme_mode={self.theme_mode}, lang={self.language})>"


from sqlalchemy import Index

# indice composto acelera filtros por leito e estado
Index('ix_simulations_bed_status', Simulation.bed_id, Simulation.status)
# indice composto acelera listar resultados por simulacao e tipo
Index('ix_results_simulation_type', Result.simulation_id, Result.result_type)
