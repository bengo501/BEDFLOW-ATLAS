#!/usr/bin/env python3
"""
compilador para linguagem .bed usando antlr
versao standalone que nao depende do bed_compiler.py
este arquivo converte arquivos .bed em params.json usando o parser antlr
"""

# importar bibliotecas padrao do python
import json  # para trabalhar com arquivos json
import hashlib  # para gerar hash sha256 dos parametros
import argparse  # para processar argumentos da linha de comando
import sys  # para acessar informacoes do sistema e sair do programa
from pathlib import Path  # para trabalhar com caminhos de arquivos de forma moderna
from typing import Dict, Any, Optional, List  # para tipagem de variaveis
from dataclasses import dataclass, asdict, field  # para criar classes de dados e converter para dicionario

# tentar importar bibliotecas do antlr
# o antlr e um gerador de parsers que cria codigo python a partir da gramatica
try:
    from antlr4 import *  # importar todas as classes principais do antlr
    from antlr4.error.ErrorListener import ErrorListener  # classe para capturar erros de parsing
    
    # adicionar pasta generated ao path do python para importar os arquivos gerados
    sys.path.append(str(Path(__file__).parent.parent / "generated"))
    
    # importar classes geradas pelo antlr a partir da gramatica bed.g4
    from BedLexer import BedLexer  # analisador lexico que quebra o texto em tokens
    from BedParser import BedParser  # analisador sintatico que verifica a estrutura
    from BedListener import BedListener  # classe base para processar a arvore de parsing
    
    ANTLR_AVAILABLE = True  # flag indicando que o antlr esta disponivel
except ImportError as e:
    # se nao conseguir importar, mostrar mensagem de erro e instrucoes
    print(f"aviso: antlr nao disponivel: {e}")
    print("para habilitar o compilador antlr (.bed -> .json):")
    print("  - instale o runtime python: pip install antlr4-python3-runtime")
    print("  - (se precisar gerar os arquivos) execute:")
    print("    java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 -o generated grammar/Bed.g4")
    ANTLR_AVAILABLE = False  # flag indicando que o antlr nao esta disponivel

    # definir stubs minimos para evitar falha de import do modulo
    # (o compile_bed_file ja bloqueia execucao quando ANTLR_AVAILABLE = False)
    class ErrorListener:  # type: ignore
        pass

    class BedListener:  # type: ignore
        pass

# estruturas de dados para parametros do leito
# cada classe representa uma secao do arquivo .bed
@dataclass
class BedGeometry:
    """classe para armazenar parametros geometricos do leito empacotado"""
    diameter: float = 0.05  # diametro interno do leito em metros
    height: float = 0.1  # altura do leito em metros
    wall_thickness: float = 0.002  # espessura da parede em metros
    clearance: float = 0.01  # espaco livre entre particulas e parede em metros
    material: str = "steel"  # material da parede do leito
    roughness: float = 0.0  # rugosidade da superficie em metros
    internal_cylinder_mode: Optional[str] = None
    visibility: Dict[str, bool] = field(default_factory=dict)

@dataclass
class DemParams:
    time_step: Optional[float] = None
    steps: Optional[int] = None
    gravity: Optional[float] = None
    stiffness: Optional[float] = None
    damping: Optional[float] = None
    friction: Optional[float] = None
    restitution: Optional[float] = None
    settle_threshold: Optional[float] = None
    max_velocity_threshold: Optional[float] = None
    seed: Optional[int] = None

@dataclass
class Lids:
    """classe para armazenar parametros das tampas do leito"""
    top_type: str = "flat"  # tipo da tampa superior (flat, hemispherical, none)
    bottom_type: str = "flat"  # tipo da tampa inferior (flat, hemispherical, none)
    top_thickness: float = 0.003  # espessura da tampa superior em metros
    bottom_thickness: float = 0.003  # espessura da tampa inferior em metros
    seal_clearance: float = 0.001  # espaco para vedacao entre tampa e leito em metros

@dataclass
class Particles:
    """classe para armazenar parametros das particulas do leito"""
    kind: str = "sphere"  # forma das particulas (sphere, cube, cylinder)
    diameter: float = 0.005  # diametro das particulas em metros
    count: int = 100  # numero total de particulas
    target_porosity: float = 0.4  # porosidade alvo do empacotamento (0.0 a 1.0)
    density: float = 2500.0  # densidade das particulas em kg/m3
    mass: float = 0.0  # massa individual das particulas em kg (0 = calculada automaticamente)
    restitution: float = 0.3  # coeficiente de restituicao (elasticidade) das particulas
    friction: float = 0.5  # coeficiente de atrito entre particulas
    rolling_friction: float = 0.1  # coeficiente de atrito de rolamento
    linear_damping: float = 0.1  # amortecimento linear das particulas
    angular_damping: float = 0.1  # amortecimento angular das particulas
    seed: int = 42  # semente para geracao de numeros aleatorios (reprodutibilidade)

@dataclass
class Packing:
    """classe para armazenar parametros do empacotamento fisico das particulas"""
    method: str = "rigid_body"  # metodo de empacotamento (rigid_body, etc)
    gravity: float = -9.81  # aceleracao da gravidade em m/s2 (negativo = para baixo)
    substeps: int = 10  # numero de subpassos por frame na simulacao fisica
    iterations: int = 10  # numero de iteracoes do solver de fisica
    damping: float = 0.1  # amortecimento geral da simulacao
    rest_velocity: float = 0.01  # velocidade de repouso em m/s (quando parar a simulacao)
    max_time: float = 5.0  # tempo maximo de simulacao em segundos
    collision_margin: float = 0.001  # margem de colisao entre objetos em metros
    gap: Optional[float] = None
    random_seed: Optional[int] = None
    max_placement_attempts: Optional[int] = None
    strict_validation: Optional[bool] = None
    step_x: Optional[float] = None
    mesh_segmentos: Optional[int] = None
    sphere_lat: Optional[int] = None
    sphere_lon: Optional[int] = None
    use_legacy_drop: Optional[bool] = None
    dem: Optional[DemParams] = None

@dataclass
class SliceConfig:
    slice_enabled: bool = True
    slice_thickness: float = 0.002
    slice_axis: str = "y"
    slice_position: float = 0.0
    keep_only_intersecting_particles: bool = True
    preserve_original_packing: bool = True
    slice_particle_policy: str = "contained"
    debug_export_gizmos: bool = False

@dataclass
class Statistical2D:
    domain_width: float = 0.05
    domain_height: float = 0.1
    target_porosity: float = 0.4
    tolerance: float = 0.02
    max_attempts: int = 50
    slice_thickness: float = 0.002
    seed: int = 42

@dataclass
class Export:
    """classe para armazenar parametros de exportacao da geometria"""
    formats: List[str] = None  # lista de formatos de exportacao (stl_binary, obj, fbx, etc)
    units: str = "m"  # unidades de medida para exportacao
    scale: float = 1.0  # fator de escala para exportacao
    wall_mode: str = "surface"  # modo das paredes (surface, solid)
    fluid_mode: str = "none"  # modo do fluido (none, cavity)
    manifold_check: bool = True  # verificar se a geometria e manifold (sem buracos)
    merge_distance: float = 0.001  # distancia para mesclar vertices proximos em metros
    
    def __post_init__(self):
        """metodo chamado apos a inicializacao da classe"""
        # se nao foi especificado formato, usar stl_binary como padrao
        if self.formats is None:
            self.formats = ["stl_binary"]

@dataclass
class CFD:
    """classe para armazenar parametros de simulacao cfd (computational fluid dynamics)"""
    regime: str = "laminar"  # regime de escoamento (laminar, turbulent_rans)
    inlet_velocity: float = 0.1  # velocidade de entrada do fluido em m/s
    fluid_density: float = 1.225  # densidade do fluido em kg/m3 (ar padrao)
    fluid_viscosity: float = 1.8e-5  # viscosidade dinamica do fluido em pa.s (ar padrao)
    max_iterations: int = 1000  # numero maximo de iteracoes do solver cfd
    convergence_criteria: float = 1e-6  # criterio de convergencia do solver
    write_fields: bool = False  # escrever campos de velocidade e pressao nos resultados

@dataclass
class BedParameters:
    """classe principal que agrupa todos os parametros do leito empacotado"""
    bed: BedGeometry = None  # parametros geometricos do leito
    lids: Lids = None  # parametros das tampas
    particles: Particles = None  # parametros das particulas
    packing: Packing = None  # parametros do empacotamento
    export: Export = None  # parametros de exportacao
    cfd: CFD = None  # parametros de simulacao cfd
    geometry_mode: Optional[str] = None
    generation_backend: Optional[str] = None
    slice: Optional[SliceConfig] = None
    statistical_2d: Optional[Statistical2D] = None
    
    def __post_init__(self):
        """metodo chamado apos a inicializacao da classe"""
        # inicializar cada secao com valores padrao se nao foi especificada
        if self.bed is None:
            self.bed = BedGeometry()
        if self.lids is None:
            self.lids = Lids()
        if self.particles is None:
            self.particles = Particles()
        if self.packing is None:
            self.packing = Packing()
        if self.export is None:
            self.export = Export()
        if self.cfd is None:
            self.cfd = CFD()

class BedErrorListener(ErrorListener):
    """classe para capturar e armazenar erros de sintaxe durante o parsing"""
    
    def __init__(self):
        """inicializar lista de erros vazia"""
        self.errors = []  # lista para armazenar mensagens de erro
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """metodo chamado quando ocorre erro de sintaxe"""
        # criar mensagem de erro formatada com linha e coluna
        error_msg = f"erro de sintaxe na linha {line}:{column} - {msg}"
        self.errors.append(error_msg)  # adicionar erro à lista

class BedCompilerListener(BedListener):
    """classe que processa a arvore de parsing do antlr e extrai os parametros"""
    
    def __init__(self):
        """inicializar com objeto de parametros vazio"""
        self.params = BedParameters()  # objeto para armazenar todos os parametros extraidos
    
    def _parse_number_with_unit(self, number: str, unit: str) -> float:
        """converter numero com unidade para unidades do sistema internacional (si)"""
        value = float(number)  # converter string para numero
        
        # conversoes para metros (unidade base de comprimento)
        if unit == "mm":
            return value / 1000.0  # milimetro para metro
        elif unit == "cm":
            return value / 100.0  # centimetro para metro
        elif unit == "m":
            return value  # ja esta em metros
        
        # conversoes para kg (unidade base de massa)
        elif unit == "g":
            return value / 1000.0  # grama para quilograma
        elif unit == "kg":
            return value  # ja esta em quilogramas
        
        # conversoes para segundos (unidade base de tempo)
        elif unit == "s":
            return value  # ja esta em segundos
        
        # conversoes para pa (unidade de pressao)
        elif unit == "Pa":
            return value  # ja esta em pascais
        
        # conversoes para n (unidade de forca)
        elif unit == "N":
            return value  # ja esta em newtons
        
        # conversoes para m/s (unidade de velocidade)
        elif unit == "m/s":
            return value  # ja esta em metros por segundo
        
        # conversoes para kg/m3 (unidade de densidade)
        elif unit == "kg/m3":
            return value  # ja esta em quilogramas por metro cubico
        
        # conversoes para pa.s (unidade de viscosidade dinamica)
        elif unit == "Pa.s":
            return value  # ja esta em pascal-segundo
        
        # conversoes para m/s2 (unidade de aceleracao)
        elif unit == "m/s2" or unit == "m/s²":
            return value  # ja esta em metros por segundo ao quadrado
        
        else:
            # se unidade nao reconhecida, retornar valor sem conversao
            return value
    
    # metodos para processar propriedades da secao bed (geometria do leito)
    def exitBedDiameter(self, ctx):
        """processar diametro do leito quando sair da regra bedDiameter"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.bed.diameter = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitBedHeight(self, ctx):
        """processar altura do leito quando sair da regra bedHeight"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.bed.height = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitBedWallThickness(self, ctx):
        """processar espessura da parede quando sair da regra bedWallThickness"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.bed.wall_thickness = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitBedClearance(self, ctx):
        """processar espaco livre quando sair da regra bedClearance"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.bed.clearance = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitBedMaterial(self, ctx):
        """processar material do leito quando sair da regra bedMaterial"""
        material = ctx.STRING().getText().strip('"')  # extrair string e remover aspas
        self.params.bed.material = material  # armazenar material
    
    def exitBedRoughness(self, ctx):
        """processar rugosidade quando sair da regra bedRoughness"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.bed.roughness = self._parse_number_with_unit(number, unit)  # converter e armazenar

    def exitBedInternalCylinderMode(self, ctx):
        self.params.bed.internal_cylinder_mode = ctx.STRING().getText().strip('"')

    def exitVisShowOuter(self, ctx):
        self.params.bed.visibility["show_outer_cylinder"] = ctx.BOOLEAN().getText() == "true"

    def exitVisShowInternal(self, ctx):
        self.params.bed.visibility["show_internal_cylinder"] = ctx.BOOLEAN().getText() == "true"

    def exitVisShowParticles(self, ctx):
        self.params.bed.visibility["show_particles"] = ctx.BOOLEAN().getText() == "true"

    def exitVisShowBooleanTools(self, ctx):
        self.params.bed.visibility["show_boolean_tools"] = ctx.BOOLEAN().getText() == "true"

    def exitVisExportBooleanTools(self, ctx):
        self.params.bed.visibility["export_boolean_tools"] = ctx.BOOLEAN().getText() == "true"
    
    # metodos para processar propriedades da secao lids (tampas do leito)
    def exitLidsTopType(self, ctx):
        """processar tipo da tampa superior quando sair da regra lidsTopType"""
        if hasattr(ctx, 'STRING') and ctx.STRING():
            # se e uma string entre aspas, extrair o conteudo
            lid_type = ctx.STRING().getText().strip('"')
        else:
            # se e um tipo predefinido, pegar apenas o texto do tipo
            lid_type = ctx.lidType().getText().strip('"')
        self.params.lids.top_type = lid_type  # armazenar tipo da tampa superior
    
    def exitLidsBottomType(self, ctx):
        """processar tipo da tampa inferior quando sair da regra lidsBottomType"""
        if hasattr(ctx, 'STRING') and ctx.STRING():
            # se e uma string entre aspas, extrair o conteudo
            lid_type = ctx.STRING().getText().strip('"')
        else:
            # se e um tipo predefinido, pegar apenas o texto do tipo
            lid_type = ctx.lidType().getText().strip('"')
        self.params.lids.bottom_type = lid_type  # armazenar tipo da tampa inferior
    
    def exitLidsTopThickness(self, ctx):
        """processar espessura da tampa superior quando sair da regra lidsTopThickness"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.lids.top_thickness = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitLidsBottomThickness(self, ctx):
        """processar espessura da tampa inferior quando sair da regra lidsBottomThickness"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.lids.bottom_thickness = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitLidsSealClearance(self, ctx):
        """processar espaco de vedacao quando sair da regra lidsSealClearance"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.lids.seal_clearance = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    # metodos para processar propriedades da secao particles (particulas do leito)
    def exitParticlesKind(self, ctx):
        """processar tipo das particulas quando sair da regra particlesKind"""
        if hasattr(ctx, 'STRING') and ctx.STRING():
            # se e uma string entre aspas, extrair o conteudo
            kind = ctx.STRING().getText().strip('"')
        else:
            # se e um tipo predefinido, pegar apenas o texto do tipo
            kind = ctx.particleKind().getText().strip('"')
        self.params.particles.kind = kind  # armazenar tipo das particulas
    
    def exitParticlesDiameter(self, ctx):
        """processar diametro das particulas quando sair da regra particlesDiameter"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.particles.diameter = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitParticlesCount(self, ctx):
        """processar numero de particulas quando sair da regra particlesCount"""
        # converter para int passando por float para tratar numeros como "100.0"
        self.params.particles.count = int(float(ctx.NUMBER().getText()))
    
    def exitParticlesTargetPorosity(self, ctx):
        """processar porosidade alvo quando sair da regra particlesTargetPorosity"""
        self.params.particles.target_porosity = float(ctx.NUMBER().getText())  # converter e armazenar
    
    def exitParticlesDensity(self, ctx):
        """processar densidade das particulas quando sair da regra particlesDensity"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.particles.density = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitParticlesMass(self, ctx):
        """processar massa das particulas quando sair da regra particlesMass"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.particles.mass = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitParticlesRestitution(self, ctx):
        """processar coeficiente de restituicao quando sair da regra particlesRestitution"""
        self.params.particles.restitution = float(ctx.NUMBER().getText())  # converter e armazenar
    
    def exitParticlesFriction(self, ctx):
        """processar coeficiente de atrito quando sair da regra particlesFriction"""
        self.params.particles.friction = float(ctx.NUMBER().getText())  # converter e armazenar
    
    def exitParticlesRollingFriction(self, ctx):
        """processar atrito de rolamento quando sair da regra particlesRollingFriction"""
        self.params.particles.rolling_friction = float(ctx.NUMBER().getText())  # converter e armazenar
    
    def exitParticlesLinearDamping(self, ctx):
        """processar amortecimento linear quando sair da regra particlesLinearDamping"""
        self.params.particles.linear_damping = float(ctx.NUMBER().getText())  # converter e armazenar
    
    def exitParticlesAngularDamping(self, ctx):
        """processar amortecimento angular quando sair da regra particlesAngularDamping"""
        self.params.particles.angular_damping = float(ctx.NUMBER().getText())  # converter e armazenar
    
    def exitParticlesSeed(self, ctx):
        """processar semente aleatoria quando sair da regra particlesSeed"""
        # converter para int passando por float para tratar numeros como "42.0"
        self.params.particles.seed = int(float(ctx.NUMBER().getText()))
    
    # metodos para processar propriedades da secao packing (empacotamento fisico)
    def exitPackingMethodProp(self, ctx):
        """processar metodo de empacotamento quando sair da regra packingMethodProp"""
        if hasattr(ctx, 'STRING') and ctx.STRING():
            # se e uma string entre aspas, extrair o conteudo
            method = ctx.STRING().getText().strip('"')
        else:
            # se e um metodo predefinido, pegar apenas o texto do metodo
            method = ctx.packingMethod().getText().strip('"')
        self.params.packing.method = method  # armazenar metodo de empacotamento
    
    def exitPackingGravity(self, ctx):
        """processar gravidade quando sair da regra packingGravity"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.packing.gravity = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitPackingSubsteps(self, ctx):
        """processar numero de subpassos quando sair da regra packingSubsteps"""
        # converter para int passando por float para tratar numeros como "10.0"
        self.params.packing.substeps = int(float(ctx.NUMBER().getText()))
    
    def exitPackingIterations(self, ctx):
        """processar numero de iteracoes quando sair da regra packingIterations"""
        # converter para int passando por float para tratar numeros como "10.0"
        self.params.packing.iterations = int(float(ctx.NUMBER().getText()))
    
    def exitPackingDamping(self, ctx):
        """processar amortecimento quando sair da regra packingDamping"""
        self.params.packing.damping = float(ctx.NUMBER().getText())  # converter e armazenar
    
    def exitPackingRestVelocity(self, ctx):
        """processar velocidade de repouso quando sair da regra packingRestVelocity"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.packing.rest_velocity = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitPackingMaxTime(self, ctx):
        """processar tempo maximo quando sair da regra packingMaxTime"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.packing.max_time = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitPackingCollisionMargin(self, ctx):
        """processar margem de colisao quando sair da regra packingCollisionMargin"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.packing.collision_margin = self._parse_number_with_unit(number, unit)  # converter e armazenar

    def _ensure_dem(self) -> DemParams:
        if self.params.packing.dem is None:
            self.params.packing.dem = DemParams()
        return self.params.packing.dem

    def exitPackingGap(self, ctx):
        unit = ctx.UNIT().getText()
        self.params.packing.gap = self._parse_number_with_unit(ctx.NUMBER().getText(), unit)

    def exitPackingRandomSeed(self, ctx):
        self.params.packing.random_seed = int(float(ctx.NUMBER().getText()))

    def exitPackingMaxAttempts(self, ctx):
        self.params.packing.max_placement_attempts = int(float(ctx.NUMBER().getText()))

    def exitPackingStrictValidation(self, ctx):
        self.params.packing.strict_validation = ctx.BOOLEAN().getText() == "true"

    def exitPackingStepX(self, ctx):
        unit = ctx.UNIT().getText()
        self.params.packing.step_x = self._parse_number_with_unit(ctx.NUMBER().getText(), unit)

    def exitPackingMeshSegmentos(self, ctx):
        self.params.packing.mesh_segmentos = int(float(ctx.NUMBER().getText()))

    def exitPackingSphereLat(self, ctx):
        self.params.packing.sphere_lat = int(float(ctx.NUMBER().getText()))

    def exitPackingSphereLon(self, ctx):
        self.params.packing.sphere_lon = int(float(ctx.NUMBER().getText()))

    def exitPackingUseLegacyDrop(self, ctx):
        self.params.packing.use_legacy_drop = ctx.BOOLEAN().getText() == "true"

    def exitDemTimeStep(self, ctx):
        d = self._ensure_dem()
        unit = ctx.UNIT().getText()
        d.time_step = self._parse_number_with_unit(ctx.NUMBER().getText(), unit)

    def exitDemSteps(self, ctx):
        self._ensure_dem().steps = int(float(ctx.NUMBER().getText()))

    def exitDemGravity(self, ctx):
        d = self._ensure_dem()
        unit = ctx.UNIT().getText()
        d.gravity = self._parse_number_with_unit(ctx.NUMBER().getText(), unit)

    def exitDemStiffness(self, ctx):
        self._ensure_dem().stiffness = float(ctx.NUMBER().getText())

    def exitDemDamping(self, ctx):
        self._ensure_dem().damping = float(ctx.NUMBER().getText())

    def exitDemFriction(self, ctx):
        self._ensure_dem().friction = float(ctx.NUMBER().getText())

    def exitDemRestitution(self, ctx):
        self._ensure_dem().restitution = float(ctx.NUMBER().getText())

    def exitDemSettleThreshold(self, ctx):
        d = self._ensure_dem()
        unit = ctx.UNIT().getText()
        d.settle_threshold = self._parse_number_with_unit(ctx.NUMBER().getText(), unit)

    def exitDemMaxVelocity(self, ctx):
        d = self._ensure_dem()
        unit = ctx.UNIT().getText()
        d.max_velocity_threshold = self._parse_number_with_unit(ctx.NUMBER().getText(), unit)

    def exitDemSeed(self, ctx):
        self._ensure_dem().seed = int(float(ctx.NUMBER().getText()))

    def exitGeometryModeProp(self, ctx):
        if hasattr(ctx, "STRING") and ctx.STRING():
            self.params.geometry_mode = ctx.STRING().getText().strip('"')
        else:
            self.params.geometry_mode = ctx.geometryMode().getText().strip('"')

    def exitGenerationBackendProp(self, ctx):
        if hasattr(ctx, "STRING") and ctx.STRING():
            self.params.generation_backend = ctx.STRING().getText().strip('"')
        else:
            self.params.generation_backend = ctx.generationBackend().getText().strip('"')

    def _ensure_slice(self) -> SliceConfig:
        if self.params.slice is None:
            self.params.slice = SliceConfig()
        return self.params.slice

    def exitSliceEnabled(self, ctx):
        self._ensure_slice().slice_enabled = ctx.BOOLEAN().getText() == "true"

    def exitSliceThickness(self, ctx):
        s = self._ensure_slice()
        unit = ctx.UNIT().getText()
        s.slice_thickness = self._parse_number_with_unit(ctx.NUMBER().getText(), unit)

    def exitSliceAxis(self, ctx):
        self._ensure_slice().slice_axis = ctx.STRING().getText().strip('"')

    def exitSlicePosition(self, ctx):
        s = self._ensure_slice()
        unit = ctx.UNIT().getText()
        s.slice_position = self._parse_number_with_unit(ctx.NUMBER().getText(), unit)

    def exitSliceKeepOnly(self, ctx):
        self._ensure_slice().keep_only_intersecting_particles = ctx.BOOLEAN().getText() == "true"

    def exitSlicePreservePacking(self, ctx):
        self._ensure_slice().preserve_original_packing = ctx.BOOLEAN().getText() == "true"

    def exitSliceParticlePolicy(self, ctx):
        self._ensure_slice().slice_particle_policy = ctx.STRING().getText().strip('"')

    def exitSliceDebugGizmos(self, ctx):
        self._ensure_slice().debug_export_gizmos = ctx.BOOLEAN().getText() == "true"

    def _ensure_statistical(self) -> Statistical2D:
        if self.params.statistical_2d is None:
            self.params.statistical_2d = Statistical2D()
        return self.params.statistical_2d

    def exitStatDomainWidth(self, ctx):
        s = self._ensure_statistical()
        unit = ctx.UNIT().getText()
        s.domain_width = self._parse_number_with_unit(ctx.NUMBER().getText(), unit)

    def exitStatDomainHeight(self, ctx):
        s = self._ensure_statistical()
        unit = ctx.UNIT().getText()
        s.domain_height = self._parse_number_with_unit(ctx.NUMBER().getText(), unit)

    def exitStatTargetPorosity(self, ctx):
        self._ensure_statistical().target_porosity = float(ctx.NUMBER().getText())

    def exitStatTolerance(self, ctx):
        self._ensure_statistical().tolerance = float(ctx.NUMBER().getText())

    def exitStatMaxAttempts(self, ctx):
        self._ensure_statistical().max_attempts = int(float(ctx.NUMBER().getText()))

    def exitStatSliceThickness(self, ctx):
        s = self._ensure_statistical()
        unit = ctx.UNIT().getText()
        s.slice_thickness = self._parse_number_with_unit(ctx.NUMBER().getText(), unit)

    def exitStatSeed(self, ctx):
        self._ensure_statistical().seed = int(float(ctx.NUMBER().getText()))
    
    # metodos para processar propriedades da secao export (exportacao da geometria)
    def exitExportFormats(self, ctx):
        """processar formatos de exportacao quando sair da regra exportFormats"""
        formats = []  # lista para armazenar formatos
        # percorrer todas as strings na lista de formatos
        for string_ctx in ctx.formatList().STRING():
            formats.append(string_ctx.getText().strip('"'))  # extrair e remover aspas
        self.params.export.formats = formats  # armazenar lista de formatos
    
    def exitExportUnits(self, ctx):
        """processar unidades de exportacao quando sair da regra exportUnits"""
        units = ctx.STRING().getText().strip('"')  # extrair string e remover aspas
        self.params.export.units = units  # armazenar unidades
    
    def exitExportScale(self, ctx):
        """processar fator de escala quando sair da regra exportScale"""
        self.params.export.scale = float(ctx.NUMBER().getText())  # converter e armazenar
    
    def exitExportWallMode(self, ctx):
        """processar modo das paredes quando sair da regra exportWallMode"""
        if hasattr(ctx, 'STRING') and ctx.STRING():
            # se e uma string entre aspas, extrair o conteudo
            mode = ctx.STRING().getText().strip('"')
        else:
            # se e um modo predefinido, pegar apenas o texto do modo
            mode = ctx.wallMode().getText().strip('"')
        self.params.export.wall_mode = mode  # armazenar modo das paredes
    
    def exitExportFluidMode(self, ctx):
        """processar modo do fluido quando sair da regra exportFluidMode"""
        if hasattr(ctx, 'STRING') and ctx.STRING():
            # se e uma string entre aspas, extrair o conteudo
            mode = ctx.STRING().getText().strip('"')
        else:
            # se e um modo predefinido, pegar apenas o texto do modo
            mode = ctx.fluidMode().getText().strip('"')
        self.params.export.fluid_mode = mode  # armazenar modo do fluido
    
    def exitExportManifoldCheck(self, ctx):
        """processar verificacao manifold quando sair da regra exportManifoldCheck"""
        # converter string "true"/"false" para boolean
        self.params.export.manifold_check = ctx.BOOLEAN().getText() == "true"
    
    def exitExportMergeDistance(self, ctx):
        """processar distancia de mesclagem quando sair da regra exportMergeDistance"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.export.merge_distance = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    # metodos para processar propriedades da secao cfd (simulacao de fluidos)
    def exitCfdRegimeProp(self, ctx):
        """processar regime de escoamento quando sair da regra cfdRegimeProp"""
        if hasattr(ctx, 'STRING') and ctx.STRING():
            # se e uma string entre aspas, extrair o conteudo
            regime = ctx.STRING().getText().strip('"')
        else:
            # se e um regime predefinido, pegar apenas o texto do regime
            regime = ctx.cfdRegime().getText().strip('"')
        self.params.cfd.regime = regime  # armazenar regime de escoamento
    
    def exitCfdInletVelocity(self, ctx):
        """processar velocidade de entrada quando sair da regra cfdInletVelocity"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.cfd.inlet_velocity = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitCfdFluidDensity(self, ctx):
        """processar densidade do fluido quando sair da regra cfdFluidDensity"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.cfd.fluid_density = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitCfdFluidViscosity(self, ctx):
        """processar viscosidade do fluido quando sair da regra cfdFluidViscosity"""
        unit = ctx.UNIT().getText()  # extrair unidade do contexto
        number = ctx.NUMBER().getText()  # extrair numero do contexto
        self.params.cfd.fluid_viscosity = self._parse_number_with_unit(number, unit)  # converter e armazenar
    
    def exitCfdMaxIterations(self, ctx):
        """processar iteracoes maximas quando sair da regra cfdMaxIterations"""
        # converter para int passando por float para tratar numeros como "1000.0"
        self.params.cfd.max_iterations = int(float(ctx.NUMBER().getText()))
    
    def exitCfdConvergenceCriteria(self, ctx):
        """processar criterio de convergencia quando sair da regra cfdConvergenceCriteria"""
        self.params.cfd.convergence_criteria = float(ctx.NUMBER().getText())  # converter e armazenar
    
    def exitCfdWriteFields(self, ctx):
        """processar escrita de campos quando sair da regra cfdWriteFields"""
        # converter string "true"/"false" para boolean
        self.params.cfd.write_fields = ctx.BOOLEAN().getText() == "true"

def _drop_none(d: Any) -> Any:
    if isinstance(d, dict):
        return {k: _drop_none(v) for k, v in d.items() if v is not None and v != {}}
    if isinstance(d, list):
        return [_drop_none(x) for x in d]
    return d


def flatten_compiled_bed_json(params_dict: Dict[str, Any]) -> Dict[str, Any]:
    """json de saida alinhado ao contrato dos motores (raiz geometry_mode, slice, etc.)."""
    out = _drop_none(dict(params_dict))
    bed = out.get("bed") or {}
    if not bed.get("visibility"):
        bed.pop("visibility", None)
    packing = out.get("packing") or {}
    dem = packing.pop("dem", None)
    if dem:
        packing["dem"] = dem
    out["packing"] = packing
    if out.get("slice"):
        sl = out["slice"]
        if sl.get("slice_enabled") is False:
            sl["slice_enabled"] = False
    return out


def compile_bed_file(input_file: str, output_file: str = None, verbose: bool = False) -> str:
    """funcao principal para compilar arquivo .bed para params.json usando antlr"""
    
    # verificar se o antlr esta disponivel
    if not ANTLR_AVAILABLE:
        raise RuntimeError("antlr nao disponivel - execute setup primeiro")
    
    # ler arquivo de entrada com codificacao utf-8
    with open(input_file, 'r', encoding='utf-8') as f:
        input_text = f.read()
    
    # criar stream de entrada para o antlr
    input_stream = InputStream(input_text)
    
    # criar analisador lexico (lexer) que quebra o texto em tokens
    lexer = BedLexer(input_stream)
    token_stream = CommonTokenStream(lexer)  # stream de tokens para o parser
    
    # criar analisador sintatico (parser) que verifica a estrutura
    parser = BedParser(token_stream)
    
    # adicionar listener personalizado para capturar erros de sintaxe
    error_listener = BedErrorListener()
    parser.removeErrorListeners()  # remover listeners padrao
    parser.addErrorListener(error_listener)  # adicionar nosso listener
    
    # fazer parsing do arquivo .bed
    tree = parser.bedFile()
    
    # verificar se houve erros de sintaxe
    if error_listener.errors:
        raise SyntaxError(f"erros de sintaxe: {'; '.join(error_listener.errors)}")
    
    # processar a arvore de parsing para extrair parametros
    listener = BedCompilerListener()  # nosso listener que extrai os dados
    walker = ParseTreeWalker()  # caminhador da arvore
    walker.walk(listener, tree)  # percorrer a arvore e extrair dados
    
    # converter objeto de parametros para dicionario
    params_dict = flatten_compiled_bed_json(asdict(listener.params))
    
    # gerar hash sha256 dos parametros para versionamento
    params_json = json.dumps(params_dict, indent=2, ensure_ascii=False)
    hash_obj = hashlib.sha256(params_json.encode())
    hash_hex = hash_obj.hexdigest()[:8]  # pegar apenas os primeiros 8 caracteres
    
    # adicionar metadados ao dicionario
    params_dict['_metadata'] = {
        'hash': hash_hex,  # hash dos parametros
        'compiler': 'bed_compiler_antlr_standalone',  # nome do compilador
        'input_file': input_file  # arquivo de entrada
    }
    
    # determinar nome do arquivo de saida
    if output_file is None:
        output_file = Path(input_file).with_suffix('.json').name
    
    # salvar arquivo json com os parametros
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(params_dict, f, indent=2, ensure_ascii=False)
    
    # mostrar informacoes se modo verboso estiver ativado
    if verbose:
        print(f"compilacao bem-sucedida (antlr): {output_file}")
        print(f"hash: {hash_hex}")
        print(f"particulas: {listener.params.particles.count}")
    
    return output_file  # retornar nome do arquivo gerado

def main():
    """funcao principal para interface de linha de comando"""
    # criar parser de argumentos da linha de comando
    parser = argparse.ArgumentParser(description='compilador .bed para params.json (antlr)')
    parser.add_argument('input', help='arquivo .bed de entrada')  # arquivo obrigatorio
    parser.add_argument('-o', '--output', help='arquivo .json de saida')  # arquivo opcional
    parser.add_argument('-v', '--verbose', action='store_true', help='modo verboso')  # flag opcional
    
    # processar argumentos da linha de comando
    args = parser.parse_args()
    
    try:
        # compilar arquivo .bed para .json
        output_file = compile_bed_file(args.input, args.output, args.verbose)
        print(f"arquivo compilado: {output_file}")
    except Exception as e:
        # se houver erro, mostrar mensagem e sair com codigo de erro
        print(f"erro na compilacao: {e}")
        sys.exit(1)

# executar funcao principal se o script for chamado diretamente
if __name__ == "__main__":
    main()
