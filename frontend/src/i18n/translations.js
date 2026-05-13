// sistema de internacionalização - português e inglês

export const translations = {
  pt: {
    // header
    appTitle: 'pipeline cfd - leitos empacotados',
    appCreativeTitle: 'bedflow atlas',
    appTagline: 'packed beds - computational fluid dynamics - dashboard - pipeline - dsl',
    footerBrandName: 'Bedflow Atlas',
    footerLogoAlt: 'logotipo Bedflow Atlas',
    backendConnectionError: 'erro de conexão com o backend',
    errorLabel: 'erro:',
    online: 'online',
    offline: 'offline',
    jobs: 'jobs',
    running: 'em execução',
    
    // navegação
    createBed: 'modo de criação',
    headerStartButton: '+ começar',
    interactiveWizard: 'wizard interativo',
    cfdSimulation: 'simulação cfd',
    results: 'resultados',
    
    // wizard
    wizardTitle: 'wizard de parametrização de leitos empacotados',
    selectMode: 'modo de criação',
    selectModeSubtitle: 'escolha uma opção abaixo',
    createHubSubtitle: 'alinhado ao «comecar» do terminal: fluxos abaixo e testes rapidos. templates, visualizacao 3d e simulacao cfd estao na sidebar.',
    hubCardCriarTitle: 'criar',
    hubCardCriarDesc: 'todos os fluxos de criação numa só grelha',
    hubCardTemplatesTitle: 'templates e editor',
    hubCardTemplatesDesc: 'json em dsl/wizard_templates ou editor .bed classico',
    hubCardQuickTitle: 'testes rapidos',
    hubCardQuickDesc: 'mesma ideia da opção 3 do terminal — mostra comandos para o fluxo guiado (dsl/wizard_quick_tests.py).',
    hubCardView3dTitle: 'visualizacao 3d',
    hubCardView3dDesc: 'lista malhas e orbitControls (three.js)',
    hubCardCfdTitle: 'simulacao cfd',
    hubCardCfdDesc: 'casos guardados e execucao',
    hubCriarBack: 'voltar ao menu comecar',
    hubCriarHeading: 'criar',
    hubCriarSubtitle: 'cinco fluxos na mesma grelha. carregar .bed ou editar .bed abre o mesmo editor; ao finalizar, o conteúdo vale como ficheiro carregado para o modo escolhido.',
    hubBasicTitle: 'criar basico',
    hubBasicDesc: 'questionário guiado; gera .bed; cfd e export opcionais.',
    hubGen3dTitle: 'geracao 3d',
    hubGen3dDesc: 'mesmo questionário; no fim gera malha e abre no blender.',
    hubPipeTitle: 'pipeline completo',
    hubPipeDesc: 'bed + blender + caso openfoam + execução do solver.',
    hubPipeBlenderCfdTitle: 'pipeline + 3d + cfd',
    hubPipeBlenderCfdDesc: 'malha e caso openfoam; nao corre o solver.',
    hubSolverOnlyTitle: 'apenas simulacao / solver',
    hubSolverOnlyDesc: 'casos em local_data/simulations; abre a lista «casos cfd» na sidebar para escolher e executar (ex.: wsl).',
    hubCfdOnlyTitle: 'apenas caso cfd',
    hubCfdOnlyDesc: 'só prepara o caso; serve quando já tens .bed definido.',
    loadBedFile: 'carregar .bed',
    editBedFile: 'editar .bed',
    bedFileModalTitle: 'ficheiro .bed para este modo',
    bedEditorSectionTitle: 'editor de .bed',
    bedEditorLoadTemplateBtn: 'carregar template base',
    bedProcessBtnInteractive: 'finalizar: compilar .bed (criar básico)',
    bedProcessBtnGen3d: 'finalizar: compilar e gerar 3d (blender)',
    bedProcessBtnPipeBlenderCfd: 'finalizar: pipeline + 3d + cfd',
    bedProcessBtnCfdOnly: 'finalizar: criar caso cfd',
    bedProcessBtnPipelineCompleto: 'finalizar: pipeline completo',
    bedProcessAlertInteractive: 'ficheiro .bed compilado com sucesso.',
    hubMoreModes: 'mais modos (só web)',
    hubMoreModesDesc: 'fluxos extra que o terminal agrupa de outra forma.',
    meshOpenStream: 'abrir stream no separador',
    meshCopyStream: 'copiar url do stream',
    meshAxes: 'eixos xyz',
    meshDesktopViewerBtn: 'visualizador versão desktop',
    meshBlenderViewerBtn: 'visualização para o blender',
    meshDesktopCmdCopied: 'comando do visualizador desktop copiado — cole no terminal na raiz do projeto.',
    meshBlenderCmdCopied: 'comando blender copiado — cole no terminal (ajuste o executável se necessário).',
    meshToolCopyFail: 'nao foi possivel copiar (permissoes do browser ou contexto inseguro).',
    meshDesktopFmtWarn: 'o visualizador desktop (open3d) aceita apenas stl, obj e ply para este atalho.',
    meshRootMissing: 'a api nao devolveu a raiz do projeto; atualize a lista ou verifique o backend.',
    meshStreamCopied: 'url do stream copiada.',
    meshStreamCopyFail: 'nao foi possivel copiar (permissoes do browser ou contexto inseguro).',
    help: 'ajuda',
    documentation: 'documentação',
    
    // modos
    interactiveMode: 'questionário interativo',
    interactiveDesc: 'responda perguntas passo a passo para criar seu leito',
    templateMode: 'editor de template',
    templateDesc: 'edite um arquivo .bed de exemplo diretamente',
    blenderMode: 'modo blender',
    blenderDesc: 'geração de modelo 3d (sem parâmetros cfd)',
    blenderInteractiveMode: 'blender interativo',
    blenderInteractiveDesc: 'gera modelo e abre automaticamente no blender',
    wizardCliModeTitle: 'wizard terminal cli',
    wizardCliModeDesc: 'abre o wizard em python no terminal (rich, menu interativo)',
    wizardCliModalTitle: 'wizard terminal cli',
    wizardCliModalIntro: 'com o backend ligado, o botão abrir terminal pede ao servidor para lançar uma janela. sem backend, abra um terminal na raiz do repositório (pasta com bed_wizard.py) e execute o comando.',
    wizardCliCopyWin: 'copiar comando (windows)',
    wizardCliCopyUnix: 'copiar comando (linux / mac / wsl)',
    wizardCliOpenTerminal: 'abrir terminal',
    wizardCliFootnote: 'obter o caminho completo e abrir o terminal pelo site requer o backend em execução. recomendado: pip install -r dsl/requirements-terminal.txt',
    wizardCliLaunchOk: 'pedido enviado ao sistema.',
    wizardCliLaunchFail: 'não foi possível abrir o terminal.',
    wizardCliLoadError: 'bed_wizard.py não encontrado no servidor (verifique o clone).',
    wizardCliFallbackHint: 'backend indisponível: estes comandos assumem que o terminal está na raiz do clone (onde está bed_wizard.py).',
    wizardCliFallbackRoot: '(raiz do repositório no seu disco)',
    wizardCliLaunchNeedsBackend: 'só disponível com o backend em execução.',
    
    // botões
    back: 'voltar',
    next: 'próximo',
    generate: 'gerar arquivo .bed',
    cancel: 'cancelar',
    confirm: 'confirmar',
    save: 'salvar',
    close: 'fechar',
    refresh: 'atualizar',
    delete: 'remover',
    view: 'visualizar resultados',
    
    // parâmetros
    bedGeometry: 'geometria do leito',
    lids: 'tampas',
    particles: 'partículas',
    packing: 'empacotamento',
    export: 'exportação',
    cfdParams: 'parâmetros cfd (opcional)',
    confirmation: 'confirmação',
    
    // cfd
    cfdTitle: 'simulações cfd',
    createNewSim: 'criar nova simulação',
    createCase: 'criar caso openfoam',
    createAndRun: 'criar e executar simulação',
    simulations: 'Simulações',
    noSimulations: 'nenhuma simulação encontrada',
    autoRefresh: 'auto-atualizar',
    
    // status
    queued: 'na fila',
    preparing: 'preparando',
    meshing: 'gerando malha',
    running: 'executando',
    completed: 'concluído',
    error: 'erro',
    
    // mensagens
    success: 'sucesso',
    warning: 'aviso',
    connectionError: 'erro de conexão com o backend',
    fileNotFound: 'arquivo não encontrado',
    compilationError: 'erro na compilação',
    
    // footer
    version: 'versão',
    project: 'tcc - eng. mecânica',
    
    // sidebar
    create: 'comecar',
    navComecarShort: 'comecar',
    simulation: 'simulação',
    pipeline: 'pipeline completo',
    casosCfd: 'casos cfd',
    monitoramentoJobs: 'monitoramento de jobs',
    configuracoes: 'configurações',
    
    // settings
    systemSettings: 'Configurações do sistema',
    theme: 'Tema',
    themeDesc: 'Escolha entre tema claro ou escuro',
    language: 'Idioma',
    languageDesc: 'Português do Brasil ou inglês',
    database: 'Banco de dados',
    databaseDesc: 'Configurações de conexão',
    simulationsDesc: 'Intervalo de atualização da lista de jobs e atalho para a página de jobs',
    
    // bed form
    parametrosLeito: 'parâmetros do leito',
    geometriaLeito: 'geometria do leito',
    diametro: 'diâmetro (m)',
    altura: 'altura (m)',
    espessuraParede: 'espessura parede (m)',
    quantidade: 'quantidade',
    diametroParticula: 'diâmetro partícula (m)',
    densidade: 'densidade (kg/m³)',
    metodo: 'método',
    gravidade: 'gravidade (m/s²)',
    tempo: 'tempo (s)',
    gerarLeito: 'gerar leito',
    
    // jobs
    todosJobs: 'todos os jobs',
    jobDetails: 'detalhes do job',
    status: 'status',
    tipo: 'tipo',
    criado: 'criado',
    duracao: 'duração',
    compilacao: 'compilação',
    modelo3d: 'modelo 3d',
    
    // results
    modelos3d: 'modelos 3d',
    simulacoesCfd: 'simulações cfd',
    baixar: 'baixar',
    visualizar: 'visualizar',
    
    // casos cfd
    casosCfdDisponiveis: 'casos cfd disponíveis',
    nome: 'nome',
    parametros: 'parâmetros',
    executar: 'executar',
    remover: 'remover'
  },
  
  en: {
    // header
    appTitle: 'cfd pipeline - packed beds',
    appCreativeTitle: 'bedflow atlas',
    appTagline: 'packed beds - computational fluid dynamics - dashboard - pipeline - dsl',
    footerBrandName: 'Bedflow Atlas',
    footerLogoAlt: 'Bedflow Atlas logo',
    backendConnectionError: 'backend connection error',
    errorLabel: 'error:',
    online: 'online',
    offline: 'offline',
    jobs: 'jobs',
    running: 'running',
    
    // navigation
    createBed: 'creation mode',
    headerStartButton: '+ start',
    interactiveWizard: 'interactive wizard',
    cfdSimulation: 'cfd simulation',
    results: 'results',
    
    // wizard
    wizardTitle: 'packed bed parameterization wizard',
    selectMode: 'creation mode',
    selectModeSubtitle: 'choose an option below',
    createHubSubtitle: 'aligned with the terminal «start» hub: flows below and quick tests. templates, 3d view, and cfd are in the sidebar.',
    hubCardCriarTitle: 'create',
    hubCardCriarDesc: 'all creation flows in one grid',
    hubCardTemplatesTitle: 'templates and editor',
    hubCardTemplatesDesc: 'json under dsl/wizard_templates or classic .bed editor',
    hubCardQuickTitle: 'quick tests',
    hubCardQuickDesc: 'same idea as terminal option 3 — shows commands for the guided flow (dsl/wizard_quick_tests.py).',
    hubCardView3dTitle: '3d visualization',
    hubCardView3dDesc: 'mesh list and orbitControls (three.js)',
    hubCardCfdTitle: 'cfd simulation',
    hubCardCfdDesc: 'saved cases and run',
    hubCriarBack: 'back to start menu',
    hubCriarHeading: 'create',
    hubCriarSubtitle: 'five flows in one grid. load .bed or edit .bed opens the same editor; on confirm, the content is applied like a loaded file for the chosen mode.',
    hubBasicTitle: 'basic create',
    hubBasicDesc: 'guided questionnaire; writes .bed; optional cfd and export.',
    hubGen3dTitle: '3d generation',
    hubGen3dDesc: 'same questionnaire; then mesh generation and opens in blender.',
    hubPipeTitle: 'full pipeline',
    hubPipeDesc: 'bed + blender + openfoam case + solver run.',
    hubPipeBlenderCfdTitle: 'pipeline + 3d + cfd',
    hubPipeBlenderCfdDesc: 'mesh and openfoam case; does not run the solver.',
    hubSolverOnlyTitle: 'simulation / solver only',
    hubSolverOnlyDesc: 'cases under local_data/simulations; opens «cfd cases» in the sidebar to pick and run (e.g. wsl).',
    hubCfdOnlyTitle: 'cfd case only',
    hubCfdOnlyDesc: 'prepares the case only; expects an existing .bed definition.',
    loadBedFile: 'load .bed',
    editBedFile: 'edit .bed',
    bedFileModalTitle: '.bed file for this mode',
    bedEditorSectionTitle: '.bed editor',
    bedEditorLoadTemplateBtn: 'load base template',
    bedProcessBtnInteractive: 'confirm: compile .bed (basic create)',
    bedProcessBtnGen3d: 'confirm: compile and generate 3d (blender)',
    bedProcessBtnPipeBlenderCfd: 'confirm: pipeline + 3d + cfd',
    bedProcessBtnCfdOnly: 'confirm: create cfd case',
    bedProcessBtnPipelineCompleto: 'confirm: full pipeline',
    bedProcessAlertInteractive: '.bed file compiled successfully.',
    hubMoreModes: 'more modes (web only)',
    hubMoreModesDesc: 'extra flows grouped differently in the terminal.',
    meshOpenStream: 'open stream in new tab',
    meshCopyStream: 'copy stream url',
    meshAxes: 'xyz axes',
    meshDesktopViewerBtn: 'desktop viewer (open3d)',
    meshBlenderViewerBtn: 'open in blender (terminal)',
    meshDesktopCmdCopied: 'desktop viewer command copied — paste in a terminal at the repo root.',
    meshBlenderCmdCopied: 'blender command copied — paste in a terminal (adjust the executable if needed).',
    meshToolCopyFail: 'could not copy (browser permissions or insecure context).',
    meshDesktopFmtWarn: 'the desktop viewer (open3d) shortcut only supports stl, obj and ply.',
    meshRootMissing: 'the api did not return the project root; refresh the list or check the backend.',
    meshStreamCopied: 'stream url copied.',
    meshStreamCopyFail: 'could not copy (browser permissions or insecure context).',
    help: 'help',
    documentation: 'documentation',
    
    // modes
    interactiveMode: 'interactive questionnaire',
    interactiveDesc: 'answer questions step by step to create your bed',
    templateMode: 'template editor',
    templateDesc: 'directly edit a .bed example file',
    blenderMode: 'blender mode',
    blenderDesc: '3d model generation (no cfd parameters)',
    blenderInteractiveMode: 'interactive blender',
    blenderInteractiveDesc: 'generates model and opens automatically in blender',
    wizardCliModeTitle: 'wizard terminal cli',
    wizardCliModeDesc: 'run the python bed wizard in a system terminal (rich ui)',
    wizardCliModalTitle: 'wizard terminal cli',
    wizardCliModalIntro: 'with the backend running, open terminal asks the server to launch a window. without it, open a terminal at the repo root (folder containing bed_wizard.py) and run the command.',
    wizardCliCopyWin: 'copy command (windows)',
    wizardCliCopyUnix: 'copy command (linux / mac / wsl)',
    wizardCliOpenTerminal: 'open terminal',
    wizardCliFootnote: 'full paths and launch-from-browser need the backend running. recommended: pip install -r dsl/requirements-terminal.txt',
    wizardCliLaunchOk: 'launch request sent.',
    wizardCliLaunchFail: 'could not open a terminal.',
    wizardCliLoadError: 'bed_wizard.py not found on the server (check the clone).',
    wizardCliFallbackHint: 'backend unavailable: these commands assume the shell cwd is the repo root (where bed_wizard.py lives).',
    wizardCliFallbackRoot: '(your local repo root)',
    wizardCliLaunchNeedsBackend: 'only available when the backend is running.',
    
    // buttons
    back: 'back',
    next: 'next',
    generate: 'generate .bed file',
    cancel: 'cancel',
    confirm: 'confirm',
    save: 'save',
    close: 'close',
    refresh: 'refresh',
    delete: 'remove',
    view: 'view results',
    
    // parameters
    bedGeometry: 'bed geometry',
    lids: 'lids',
    particles: 'particles',
    packing: 'packing',
    export: 'export',
    cfdParams: 'cfd parameters (optional)',
    confirmation: 'confirmation',
    
    // cfd
    cfdTitle: 'cfd simulations',
    createNewSim: 'create new simulation',
    createCase: 'create openfoam case',
    createAndRun: 'create and run simulation',
    simulations: 'Simulations',
    noSimulations: 'no simulations found',
    autoRefresh: 'auto-refresh',
    
    // status
    queued: 'queued',
    preparing: 'preparing',
    meshing: 'meshing',
    running: 'running',
    completed: 'completed',
    error: 'error',
    
    // messages
    success: 'success',
    warning: 'warning',
    connectionError: 'backend connection error',
    fileNotFound: 'file not found',
    compilationError: 'compilation error',
    
    // footer
    version: 'version',
    project: 'senior project - mechanical eng.',
    
    // sidebar
    create: 'start',
    navComecarShort: 'start',
    simulation: 'simulation',
    pipeline: 'complete pipeline',
    casosCfd: 'cfd cases',
    monitoramentoJobs: 'job monitoring',
    configuracoes: 'settings',
    
    // settings
    systemSettings: 'System settings',
    theme: 'Theme',
    themeDesc: 'Choose between light or dark theme',
    language: 'Language',
    languageDesc: 'Brazilian Portuguese or English',
    database: 'Database',
    databaseDesc: 'Connection settings',
    simulationsDesc: 'Jobs list refresh interval and shortcut to the jobs page',
    
    // bed form
    parametrosLeito: 'bed parameters',
    geometriaLeito: 'bed geometry',
    diametro: 'diameter (m)',
    altura: 'height (m)',
    espessuraParede: 'wall thickness (m)',
    quantidade: 'quantity',
    diametroParticula: 'particle diameter (m)',
    densidade: 'density (kg/m³)',
    metodo: 'method',
    gravidade: 'gravity (m/s²)',
    tempo: 'time (s)',
    gerarLeito: 'generate bed',
    
    // jobs
    todosJobs: 'all jobs',
    jobDetails: 'job details',
    status: 'status',
    tipo: 'type',
    criado: 'created',
    duracao: 'duration',
    compilacao: 'compilation',
    modelo3d: '3d model',
    
    // results
    modelos3d: '3d models',
    simulacoesCfd: 'cfd simulations',
    baixar: 'download',
    visualizar: 'view',
    
    // casos cfd
    casosCfdDisponiveis: 'available cfd cases',
    nome: 'name',
    parametros: 'parameters',
    executar: 'run',
    remover: 'remove'
  }
};

// hook para usar traduções
export const useTranslation = (language) => {
  const t = (key) => {
    const keys = key.split('.');
    let value = translations[language];
    
    for (const k of keys) {
      value = value?.[k];
    }
    
    return value || key;
  };
  
  return { t };
};

