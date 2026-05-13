import { useState, useMemo } from 'react';
import BedPreview3D from './BedPreview3D';
import { HelpModal, DocsModal } from './WizardHelpers';
import ThemeIcon from './ThemeIcon';
import BackendConnectionError from './BackendConnectionError';
import { useLanguage } from '../context/LanguageContext';
import {
  getWizardCliInstructions,
  launchWizardCliTerminal,
  postBedWizard,
  generateModel,
  postPipelineFullSimulation,
  getBedTemplateDefault,
  postBedProcess,
  pollJobUntilDone,
  postCfdCreateCase,
  postCfdCreateCaseOnly,
  parseApiError,
} from '../services/api';
import '../styles/BedWizard.css';

const BedWizard = ({ onNavigateTab } = {}) => {
  const { language, t } = useLanguage();
  const [step, setStep] = useState(0);
  const [hubView, setHubView] = useState('comecar');
  const [mode, setMode] = useState(null);
  const [params, setParams] = useState({
    bed: {
      diameter: '0.05',
      height: '0.1',
      wall_thickness: '0.002',
      clearance: '0.01',
      material: 'steel',
      roughness: '0.0'
    },
    lids: {
      top_type: 'flat',
      bottom_type: 'flat',
      top_thickness: '0.003',
      bottom_thickness: '0.003',
      seal_clearance: '0.001'
    },
    particles: {
      kind: 'sphere',
      diameter: '0.005',
      count: '100',
      target_porosity: '0.4',
      density: '2500.0',
      mass: '0.0',
      restitution: '0.3',
      friction: '0.5',
      rolling_friction: '0.1',
      linear_damping: '0.1',
      angular_damping: '0.1',
      seed: '42'
    },
    packing: {
      method: 'rigid_body',
      gravity: '-9.81',
      substeps: '10',
      iterations: '10',
      damping: '0.1',
      rest_velocity: '0.01',
      max_time: '5.0',
      collision_margin: '0.001'
    },
    export: {
      formats: ['stl_binary', 'blend'],
      units: 'm',
      scale: '1.0',
      wall_mode: 'surface',
      fluid_mode: 'none',
      manifold_check: true,
      merge_distance: '0.001'
    },
    cfd: null
  });
  const [includeCFD, setIncludeCFD] = useState(false);
  const [fileName, setFileName] = useState('meu_leito.bed');

  // informações de ajuda para cada parâmetro
  const paramHelp = {
    'bed.diameter': {
      desc: 'diâmetro interno do leito cilíndrico',
      min: 0.01, max: 2.0, unit: 'm',
      exemplo: 'leito de 5cm = 0.05m'
    },
    'bed.height': {
      desc: 'altura total do leito cilíndrico',
      min: 0.01, max: 5.0, unit: 'm',
      exemplo: 'leito de 10cm = 0.1m'
    },
    'bed.wall_thickness': {
      desc: 'espessura da parede do cilindro',
      min: 0.0001, max: 0.1, unit: 'm',
      exemplo: 'parede de 2mm = 0.002m'
    },
    'particles.count': {
      desc: 'quantidade total de partículas',
      min: 1, max: 10000, unit: '',
      exemplo: '100 partículas = empacotamento rápido'
    },
    'particles.diameter': {
      desc: 'diâmetro das partículas esféricas',
      min: 0.0001, max: 0.5, unit: 'm',
      exemplo: 'partícula de 5mm = 0.005m'
    }
  };

  const [showHelp, setShowHelp] = useState(false);
  const [helpSection, setHelpSection] = useState(null);
  const [showDocs, setShowDocs] = useState(false);
  const [showBedFileOptions, setShowBedFileOptions] = useState(false);
  const [bedFileContent, setBedFileContent] = useState('');
  const [bedFileName, setBedFileName] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [wizardConnectionError, setWizardConnectionError] = useState(null);
  const [showWizardCliModal, setShowWizardCliModal] = useState(false);
  const [wizardCliInfo, setWizardCliInfo] = useState(null);
  const [wizardCliError, setWizardCliError] = useState(null);
  const [wizardCliBusy, setWizardCliBusy] = useState(false);
  const [wizardCliLaunchMsg, setWizardCliLaunchMsg] = useState('');

  const steps = useMemo(
    () => [
      { title: t('selectMode'), section: 'mode' },
      { title: t('bedGeometry'), section: 'bed' },
      { title: t('lids'), section: 'lids' },
      { title: t('particles'), section: 'particles' },
      { title: t('packing'), section: 'packing' },
      { title: t('export'), section: 'export' },
      { title: t('cfdParams'), section: 'cfd' },
      { title: t('confirmation'), section: 'confirm' },
    ],
    [language]
  );

  const handleModeSelect = (selectedMode) => {
    setMode(selectedMode);
    setStep(1);
  };

  const buildWizardCliFallback = () => ({
    project_root: t('wizardCliFallbackRoot'),
    windows_cmd: 'python bed_wizard.py',
    unix_sh: 'python3 bed_wizard.py',
    script_exists: true,
    hint: t('wizardCliFallbackHint'),
    offline: true,
  });

  const openWizardCliModal = async () => {
    setShowWizardCliModal(true);
    setWizardCliError(null);
    setWizardCliLaunchMsg('');
    setWizardCliInfo(null);
    try {
      const data = await getWizardCliInstructions();
      setWizardCliInfo({ ...data, offline: false });
      if (!data.script_exists) {
        setWizardCliError(t('wizardCliLoadError'));
      }
    } catch {
      setWizardCliInfo(buildWizardCliFallback());
    }
  };

  const handleLaunchWizardCli = async () => {
    setWizardCliBusy(true);
    setWizardCliLaunchMsg('');
    try {
      await launchWizardCliTerminal();
      setWizardCliLaunchMsg(t('wizardCliLaunchOk'));
    } catch {
      setWizardCliLaunchMsg(t('wizardCliLaunchFail'));
    } finally {
      setWizardCliBusy(false);
    }
  };

  const handleInputChange = (section, field, value) => {
    setParams(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleNext = () => {
    if (step < steps.length - 1) {
      // sempre ir para próximo passo sequencialmente
      // não pular mais automaticamente
      setStep(step + 1);
    }
  };

  const handlePrev = () => {
    if (step > 0) {
      // sempre voltar sequencialmente
      setStep(step - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setWizardConnectionError(null);
      const bedData = {
        mode: mode,
        fileName: fileName,
        params: params
      };

      const result = await postBedWizard(bedData);
      alert(`sucesso! arquivo ${fileName} criado\nJSON gerado: ${result.json_file}`);

      if (mode === 'blender' || mode === 'blender_interactive') {
        if (confirm('deseja gerar o modelo 3D agora?')) {
          await generateModel(result.json_file, mode === 'blender_interactive');
          alert('geração do modelo 3D iniciada (acompanhe em jobs)');
        }
      }

      if (mode === 'pipeline_completo') {
        if (confirm('deseja executar o pipeline completo agora? (modelo 3d + simulação cfd)')) {
          const pipelineResult = await postPipelineFullSimulation({
            bed: params.bed,
            lids: params.lids,
            particles: params.particles,
            packing: params.packing,
            export: params.export,
            cfd: includeCFD ? {
              solver: 'simpleFoam',
              turbulence: 'kEpsilon',
              convergence: 1e-6,
              max_iterations: 1000
            } : null
          });
          alert(`pipeline completo iniciado!\njob_id: ${pipelineResult.job_id}\nmonitore o progresso na seção 'jobs'`);
        }
      }

      setStep(0);
      setMode(null);
      setHubView('comecar');
    } catch (error) {
      console.error('erro:', error);
      alert(parseApiError(error) || 'erro ao criar arquivo .bed');
      setWizardConnectionError(t('backendConnectionError'));
    }
  };

  const goHubTab = (tab) => {
    if (typeof onNavigateTab === 'function') onNavigateTab(tab);
  };

  const bedProcessActionLabel = () => {
    if (mode === 'interactive') return t('bedProcessBtnInteractive');
    if (mode === 'blender' || mode === 'blender_interactive') return t('bedProcessBtnGen3d');
    if (mode === 'pipeline_blender_cfd') return t('bedProcessBtnPipeBlenderCfd');
    if (mode === 'cfd_only') return t('bedProcessBtnCfdOnly');
    if (mode === 'pipeline_completo') return t('bedProcessBtnPipelineCompleto');
    return t('bedProcessBtnPipelineCompleto');
  };

  const renderModeSelection = () => {
    const bedFileButtons = (modeKey) => (
      <div className="mode-options">
        <button
          type="button"
          className="btn-mode-option"
          onClick={(e) => {
            e.stopPropagation();
            setMode(modeKey);
            setShowBedFileOptions(true);
          }}
        >
          <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="" className="btn-icon" />
          {t('loadBedFile')}
        </button>
        <button
          type="button"
          className="btn-mode-option"
          onClick={(e) => {
            e.stopPropagation();
            setMode(modeKey);
            void loadDefaultBedTemplate();
            setShowBedFileOptions(true);
          }}
        >
          <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="" className="btn-icon" />
          {t('editBedFile')}
        </button>
      </div>
    );

    const cardKey =
      (fn) => (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          fn();
        }
      };

    if (hubView === 'criar') {
      return (
        <div className="mode-selection">
          <div className="mode-header">
            <div className="mode-header-titles">
              <button type="button" className="hub-back-btn" onClick={() => setHubView('comecar')}>
                {t('hubCriarBack')}
              </button>
              <h2>
                <ThemeIcon light="bedLight.png" dark="bedDark.png" alt="" className="title-icon" />
                {t('hubCriarHeading')}
              </h2>
              <p className="mode-header-subtitle">{t('hubCriarSubtitle')}</p>
            </div>
          </div>
          <div className="mode-cards mode-cards-terminal mode-cards-criar-all">
            <div
              className="mode-card"
              role="button"
              tabIndex={0}
              onClick={() => handleModeSelect('interactive')}
              onKeyDown={cardKey(() => handleModeSelect('interactive'))}
            >
              <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="" className="mode-icon-small" />
              <h3>{t('hubBasicTitle')}</h3>
              <p className="mode-card-desc">{t('hubBasicDesc')}</p>
              {bedFileButtons('interactive')}
            </div>
            <div
              className="mode-card"
              role="button"
              tabIndex={0}
              onClick={() => handleModeSelect('blender_interactive')}
              onKeyDown={cardKey(() => handleModeSelect('blender_interactive'))}
            >
              <ThemeIcon light="blenderLight.png" dark="blender-svgrepo-com.svg" alt="" className="mode-icon-small" />
              <h3>{t('hubGen3dTitle')}</h3>
              <p className="mode-card-desc">{t('hubGen3dDesc')}</p>
              {bedFileButtons('blender_interactive')}
            </div>
            <div
              className="mode-card"
              role="button"
              tabIndex={0}
              onClick={() => handleModeSelect('pipeline_completo')}
              onKeyDown={cardKey(() => handleModeSelect('pipeline_completo'))}
            >
              <ThemeIcon light="pipelineLight.png" dark="pipeline.png" alt="" className="mode-icon-small" />
              <h3>{t('hubPipeTitle')}</h3>
              <p className="mode-card-desc">{t('hubPipeDesc')}</p>
              {bedFileButtons('pipeline_completo')}
            </div>
            <div
              className="mode-card"
              role="button"
              tabIndex={0}
              onClick={() => handleModeSelect('pipeline_blender_cfd')}
              onKeyDown={cardKey(() => handleModeSelect('pipeline_blender_cfd'))}
            >
              <div className="mode-icon-combo">
                <ThemeIcon light="blenderLight.png" dark="blender-svgrepo-com.svg" alt="" className="mode-icon-small" />
                <span className="plus-symbol">+</span>
                <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="" className="mode-icon-small" />
              </div>
              <h3>{t('hubPipeBlenderCfdTitle')}</h3>
              <p className="mode-card-desc">{t('hubPipeBlenderCfdDesc')}</p>
              {bedFileButtons('pipeline_blender_cfd')}
            </div>
            <div
              className="mode-card"
              role="button"
              tabIndex={0}
              onClick={() => handleModeSelect('cfd_only')}
              onKeyDown={cardKey(() => handleModeSelect('cfd_only'))}
            >
              <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="" className="mode-icon-small" />
              <h3>{t('hubCfdOnlyTitle')}</h3>
              <p className="mode-card-desc">{t('hubCfdOnlyDesc')}</p>
              {bedFileButtons('cfd_only')}
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="mode-selection">
        <div className="mode-header">
          <div className="mode-header-titles">
            <h2>
              <ThemeIcon light="bedLight.png" dark="bedDark.png" alt={t('createBed')} className="title-icon" />
              {t('selectMode')}
            </h2>
            <p className="mode-header-subtitle">{t('createHubSubtitle')}</p>
          </div>
        </div>

        <div className="mode-cards mode-cards-terminal">
          <div className="mode-card" role="button" tabIndex={0} onClick={() => setHubView('criar')} onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setHubView('criar'); } }}>
            <ThemeIcon light="bedLight.png" dark="bedDark.png" alt="" className="mode-icon-small" />
            <h3>{t('hubCardCriarTitle')}</h3>
            <p>{t('hubCardCriarDesc')}</p>
          </div>
          <div className="mode-card" role="button" tabIndex={0} onClick={() => goHubTab('templates')} onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); goHubTab('templates'); } }}>
            <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="" className="mode-icon-small" />
            <h3>{t('hubCardTemplatesTitle')}</h3>
            <p>{t('hubCardTemplatesDesc')}</p>
          </div>
          <div className="mode-card" role="button" tabIndex={0} onClick={() => { void openWizardCliModal(); }} onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); void openWizardCliModal(); } }}>
            <ThemeIcon light="runLight.png" dark="runLight.png" alt="" className="mode-icon-small" />
            <h3>{t('hubCardQuickTitle')}</h3>
            <p>{t('hubCardQuickDesc')}</p>
          </div>
          <div className="mode-card" role="button" tabIndex={0} onClick={() => goHubTab('mesh-viewer')} onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); goHubTab('mesh-viewer'); } }}>
            <ThemeIcon light="cfd_gear_white.png" dark="cfd_gear_white.png" alt="" className="mode-icon-small" />
            <h3>{t('hubCardView3dTitle')}</h3>
            <p>{t('hubCardView3dDesc')}</p>
          </div>
          <div className="mode-card" role="button" tabIndex={0} onClick={() => goHubTab('cfd')} onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); goHubTab('cfd'); } }}>
            <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="" className="mode-icon-small" />
            <h3>{t('hubCardCfdTitle')}</h3>
            <p>{t('hubCardCfdDesc')}</p>
          </div>
        </div>
      </div>
    );
  };

  // renderizar seção bed
  const renderBedSection = () => (
    <div className="form-section">
      <h2>geometria do leito</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>diâmetro (m)</label>
          <input
            type="number"
            step="0.001"
            value={params.bed.diameter}
            onChange={(e) => handleInputChange('bed', 'diameter', e.target.value)}
          />
          <small>ex: 0.05m = 5cm</small>
        </div>
        
        <div className="form-group">
          <label>altura (m)</label>
          <input
            type="number"
            step="0.001"
            value={params.bed.height}
            onChange={(e) => handleInputChange('bed', 'height', e.target.value)}
          />
          <small>ex: 0.1m = 10cm</small>
        </div>
        
        <div className="form-group">
          <label>espessura da parede (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.bed.wall_thickness}
            onChange={(e) => handleInputChange('bed', 'wall_thickness', e.target.value)}
          />
          <small>ex: 0.002m = 2mm</small>
        </div>
        
        <div className="form-group">
          <label>folga superior (m)</label>
          <input
            type="number"
            step="0.001"
            value={params.bed.clearance}
            onChange={(e) => handleInputChange('bed', 'clearance', e.target.value)}
          />
          <small>espaço livre acima das partículas</small>
        </div>
        
        <div className="form-group">
          <label>material da parede</label>
          <input
            type="text"
            value={params.bed.material}
            onChange={(e) => handleInputChange('bed', 'material', e.target.value)}
          />
          <small>ex: steel, aluminum, glass</small>
        </div>
        
        <div className="form-group">
          <label>rugosidade (m) - opcional</label>
          <input
            type="number"
            step="0.0001"
            value={params.bed.roughness}
            onChange={(e) => handleInputChange('bed', 'roughness', e.target.value)}
          />
          <small>0.0 = superfície lisa</small>
        </div>
      </div>
    </div>
  );

  // renderizar seção lids
  const renderLidsSection = () => (
    <div className="form-section">
      <h2>tampas</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>tipo tampa superior</label>
          <select
            value={params.lids.top_type}
            onChange={(e) => handleInputChange('lids', 'top_type', e.target.value)}
          >
            <option value="flat">plana</option>
            <option value="hemispherical">hemisférica</option>
            <option value="none">sem tampa</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>tipo tampa inferior</label>
          <select
            value={params.lids.bottom_type}
            onChange={(e) => handleInputChange('lids', 'bottom_type', e.target.value)}
          >
            <option value="flat">plana</option>
            <option value="hemispherical">hemisférica</option>
            <option value="none">sem tampa</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>espessura tampa superior (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.lids.top_thickness}
            onChange={(e) => handleInputChange('lids', 'top_thickness', e.target.value)}
          />
          <small>ex: 0.003m = 3mm</small>
        </div>
        
        <div className="form-group">
          <label>espessura tampa inferior (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.lids.bottom_thickness}
            onChange={(e) => handleInputChange('lids', 'bottom_thickness', e.target.value)}
          />
          <small>ex: 0.003m = 3mm</small>
        </div>
      </div>
    </div>
  );

  // renderizar seção particles
  const renderParticlesSection = () => (
    <div className="form-section">
      <h2>partículas</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>tipo de partícula</label>
          <select
            value={params.particles.kind}
            onChange={(e) => handleInputChange('particles', 'kind', e.target.value)}
          >
            <option value="sphere">esfera</option>
            <option value="cube">cubo</option>
            <option value="cylinder">cilindro</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>diâmetro (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.particles.diameter}
            onChange={(e) => handleInputChange('particles', 'diameter', e.target.value)}
          />
          <small>ex: 0.005m = 5mm</small>
        </div>
        
        <div className="form-group">
          <label>quantidade</label>
          <input
            type="number"
            value={params.particles.count}
            onChange={(e) => handleInputChange('particles', 'count', e.target.value)}
          />
          <small>100 = rápido, 1000 = detalhado</small>
        </div>
        
        <div className="form-group">
          <label>densidade (kg/m³)</label>
          <input
            type="number"
            step="10"
            value={params.particles.density}
            onChange={(e) => handleInputChange('particles', 'density', e.target.value)}
          />
          <small>vidro = 2500, aço = 7850</small>
        </div>
        
        <div className="form-group">
          <label>seed para reproducibilidade</label>
          <input
            type="number"
            value={params.particles.seed}
            onChange={(e) => handleInputChange('particles', 'seed', e.target.value)}
          />
          <small>42 = resultado reproduzível</small>
        </div>
      </div>
      
      <details className="advanced-params">
        <summary>parâmetros avançados de física</summary>
        <div className="form-grid">
          <div className="form-group">
            <label>restituição (quique)</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={params.particles.restitution}
              onChange={(e) => handleInputChange('particles', 'restitution', e.target.value)}
            />
            <small>0.0 = sem quique, 1.0 = quique total</small>
          </div>
          
          <div className="form-group">
            <label>atrito</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={params.particles.friction}
              onChange={(e) => handleInputChange('particles', 'friction', e.target.value)}
            />
            <small>0.5 = atrito moderado</small>
          </div>
        </div>
      </details>
    </div>
  );

  // renderizar seção packing
  const renderPackingSection = () => (
    <div className="form-section">
      <h2>empacotamento</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>método</label>
          <select
            value={params.packing.method}
            onChange={(e) => handleInputChange('packing', 'method', e.target.value)}
          >
            <option value="rigid_body">corpo rígido (física)</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>gravidade (m/s²)</label>
          <input
            type="number"
            step="0.1"
            value={params.packing.gravity}
            onChange={(e) => handleInputChange('packing', 'gravity', e.target.value)}
          />
          <small>terra = -9.81, lua = -1.62</small>
        </div>
        
        <div className="form-group">
          <label>sub-passos</label>
          <input
            type="number"
            value={params.packing.substeps}
            onChange={(e) => handleInputChange('packing', 'substeps', e.target.value)}
          />
          <small>10 = boa precisão</small>
        </div>
        
        <div className="form-group">
          <label>tempo máximo (s)</label>
          <input
            type="number"
            step="0.5"
            value={params.packing.max_time}
            onChange={(e) => handleInputChange('packing', 'max_time', e.target.value)}
          />
          <small>5s = suficiente para empacotamento</small>
        </div>
      </div>
    </div>
  );

  // renderizar seção export
  const renderExportSection = () => {
    const formatosDisponiveis = [
      { value: 'blend', label: 'blend (nativo blender)' },
      { value: 'gltf', label: 'gltf (web - multiplos arquivos)' },
      { value: 'glb', label: 'glb (web - arquivo unico)' },
      { value: 'obj', label: 'obj (universal)' },
      { value: 'fbx', label: 'fbx (unity, unreal)' },
      { value: 'stl', label: 'stl (impressao 3d)' }
    ];

    const toggleFormato = (formato) => {
      const formatos = params.export.formats || [];
      const novosFormatos = formatos.includes(formato)
        ? formatos.filter(f => f !== formato)
        : [...formatos, formato];
      
      handleInputChange('export', 'formats', novosFormatos);
    };

    return (
      <div className="form-section">
        <h2>exportação</h2>
        
        <div className="form-group">
          <label>formatos de exportação</label>
          <div className="checkbox-group-formats">
            {formatosDisponiveis.map(({ value, label }) => (
              <label key={value} className="checkbox-format">
                <input
                  type="checkbox"
                  checked={params.export.formats?.includes(value) || false}
                  onChange={() => toggleFormato(value)}
                />
                {label}
              </label>
            ))}
          </div>
          <small>
            selecionados: {params.export.formats?.length || 0} formato(s) - 
            recomendado: blend + glb + obj
          </small>
        </div>
        
        <div className="form-grid">
          <div className="form-group">
            <label>modo da parede</label>
            <select
              value={params.export.wall_mode}
              onChange={(e) => handleInputChange('export', 'wall_mode', e.target.value)}
            >
              <option value="surface">superfície (recomendado)</option>
              <option value="solid">sólido</option>
            </select>
            <small>surface = melhor para cfd</small>
          </div>
          
          <div className="form-group">
            <label>modo do fluido</label>
            <select
              value={params.export.fluid_mode}
              onChange={(e) => handleInputChange('export', 'fluid_mode', e.target.value)}
            >
              <option value="none">nenhum (recomendado)</option>
              <option value="cavity">cavidade</option>
            </select>
          </div>
          
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={params.export.manifold_check}
                onChange={(e) => handleInputChange('export', 'manifold_check', e.target.checked)}
              />
              verificar manifold (recomendado)
            </label>
            <small>garante integridade da malha</small>
          </div>
        </div>
      </div>
    );
  };

  // renderizar confirmação
  const renderConfirmation = () => (
    <div className="form-section confirmation">
      <h2>confirmação dos parâmetros</h2>
      
      {/* preview 3D */}
      <BedPreview3D params={params} />
      
      <div className="summary-grid">
        <div className="summary-card">
          <h3>geometria</h3>
          <p>leito: {params.bed.diameter}m × {params.bed.height}m</p>
          <p>parede: {params.bed.material}</p>
        </div>
        
        <div className="summary-card">
          <h3>partículas</h3>
          <p>{params.particles.count} {params.particles.kind}</p>
          <p>diâmetro: {params.particles.diameter}m</p>
          <p>densidade: {params.particles.density} kg/m³</p>
        </div>
        
        <div className="summary-card">
          <h3>empacotamento</h3>
          <p>{params.packing.method}</p>
          <p>gravidade: {params.packing.gravity} m/s²</p>
        </div>
        
        <div className="summary-card">
          <h3>exportação</h3>
          <p>formatos: {params.export.formats.join(', ')}</p>
          <p>modo: {params.export.wall_mode}</p>
        </div>
      </div>
      
      <div className="form-group">
        <label>nome do arquivo</label>
        <input
          type="text"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
          placeholder="meu_leito.bed"
        />
      </div>
    </div>
  );



  // carregar arquivo .bed
  const handleBedFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.bed')) {
      setUploadedFile(file);
      setBedFileName(file.name);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setBedFileContent(e.target.result);
      };
      reader.readAsText(file);
    } else {
      alert('por favor, selecione um arquivo .bed válido');
    }
  };

  // carregar template padrão
  const loadDefaultBedTemplate = async () => {
    try {
      setWizardConnectionError(null);
      const data = await getBedTemplateDefault();
      setBedFileContent(data.content);
      setBedFileName('template_padrao.bed');
      setUploadedFile(null);
    } catch (error) {
      console.error('erro:', error);
      alert(parseApiError(error) || 'erro ao carregar template padrão');
      setWizardConnectionError(t('backendConnectionError'));
    }
  };

  // processar arquivo .bed carregado
  const processBedFile = async () => {
    if (!bedFileContent.trim()) {
      alert('arquivo .bed está vazio');
      return;
    }

    try {
      setWizardConnectionError(null);
      const result = await postBedProcess({
        content: bedFileContent,
        filename: bedFileName || 'leito_custom.bed'
      });

      if (mode === 'interactive') {
        alert(
          `${t('bedProcessAlertInteractive')}\njson: ${result.json_file}`,
        );
      }

      if (mode === 'blender_interactive') {
        await generateModel(result.json_file, true);
        alert('geração do modelo 3D iniciada (blender pode abrir no servidor)');
      }

      if (mode === 'pipeline_blender_cfd') {
        const genStart = await generateModel(result.json_file, false);
        const jobFinal = await pollJobUntilDone(genStart.job_id);
        const blendRel =
          jobFinal.metadata?.blend_file ||
          jobFinal.metadata?.geometry_file ||
          (jobFinal.output_files && jobFinal.output_files[0]);
        if (!blendRel) {
          throw new Error('job de modelo não devolveu caminho blend/stl');
        }
        const cfdResult = await postCfdCreateCase({
          blend_file: blendRel,
          json_file: result.json_file,
          case_name: `leito_${Date.now()}`
        });
        alert(`pipeline blender + CFD concluído!\nmodelo: ${blendRel}\ncaso CFD: ${cfdResult.case_dir}`);
      }

      if (mode === 'cfd_only') {
        const cfdResult = await postCfdCreateCaseOnly({
          json_file: result.json_file,
          case_name: `leito_${Date.now()}`
        });
        alert(`caso CFD criado com sucesso!\ncaso: ${cfdResult.case_dir}`);
      }

      if (mode === 'pipeline_completo') {
        const pipelineResult = await postPipelineFullSimulation({
          json_file: result.json_file,
          bed_file: result.bed_file || ''
        });
        alert(`pipeline completo iniciado!\njob_id: ${pipelineResult.job_id}`);
      }

      setStep(0);
      setMode(null);
      setHubView('comecar');
      setShowBedFileOptions(false);
      setBedFileContent('');
      setBedFileName('');
      setUploadedFile(null);
    } catch (error) {
      console.error('erro:', error);
      alert(parseApiError(error) || 'erro ao processar arquivo .bed');
      setWizardConnectionError(t('backendConnectionError'));
    }
  };

  return (
    <div className="bed-wizard">
      {wizardConnectionError && (
        <BackendConnectionError message={wizardConnectionError} />
      )}
      {/* modais */}
      <HelpModal 
        show={showHelp} 
        onClose={() => setShowHelp(false)} 
        section={helpSection}
        paramHelp={paramHelp}
      />
      
      <DocsModal 
        show={showDocs} 
        onClose={() => setShowDocs(false)} 
      />
      

      {/* modal de opções de arquivo .bed */}
      {showWizardCliModal && (
        <div
          className="modal-overlay"
          role="presentation"
          onClick={() => {
            setShowWizardCliModal(false);
            setWizardCliInfo(null);
            setWizardCliError(null);
            setWizardCliLaunchMsg('');
          }}
        >
          <div
            className="modal-content bed-file-options wizard-cli-modal"
            role="dialog"
            aria-labelledby="wizard-cli-title"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <h2 id="wizard-cli-title">{t('wizardCliModalTitle')}</h2>
              <button
                type="button"
                className="btn-close"
                onClick={() => {
                  setShowWizardCliModal(false);
                  setWizardCliInfo(null);
                  setWizardCliError(null);
                  setWizardCliLaunchMsg('');
                }}
              >
                ×
              </button>
            </div>
            <div className="wizard-cli-body">
              <p className="wizard-cli-intro">{t('wizardCliModalIntro')}</p>
              {wizardCliError && <p className="wizard-cli-err">{wizardCliError}</p>}
              {wizardCliInfo && (
                <div className="wizard-cli-commands">
                  <p className="wizard-cli-hint">{wizardCliInfo.hint}</p>
                  <label>windows (cmd)</label>
                  <pre>{wizardCliInfo.windows_cmd}</pre>
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => navigator.clipboard.writeText(wizardCliInfo.windows_cmd)}
                  >
                    {t('wizardCliCopyWin')}
                  </button>
                  <label>linux / mac / wsl (bash)</label>
                  <pre>{wizardCliInfo.unix_sh}</pre>
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => navigator.clipboard.writeText(wizardCliInfo.unix_sh)}
                  >
                    {t('wizardCliCopyUnix')}
                  </button>
                  <p className="wizard-cli-root">
                    <span>project_root: </span>
                    {wizardCliInfo.project_root}
                  </p>
                </div>
              )}
              {wizardCliLaunchMsg && <p className="wizard-cli-launch-msg">{wizardCliLaunchMsg}</p>}
              <p className="wizard-cli-foot">{t('wizardCliFootnote')}</p>
              <div className="wizard-cli-actions">
                <button
                  type="button"
                  className="btn-primary"
                  title={wizardCliInfo?.offline ? t('wizardCliLaunchNeedsBackend') : undefined}
                  disabled={
                    wizardCliBusy ||
                    !wizardCliInfo?.script_exists ||
                    wizardCliInfo?.offline
                  }
                  onClick={() => {
                    void handleLaunchWizardCli();
                  }}
                >
                  {t('wizardCliOpenTerminal')}
                </button>
                <button
                  type="button"
                  className="btn-cancel"
                  onClick={() => {
                    setShowWizardCliModal(false);
                    setWizardCliInfo(null);
                    setWizardCliError(null);
                    setWizardCliLaunchMsg('');
                  }}
                >
                  {t('close')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showBedFileOptions && (
        <div className="modal-overlay">
          <div className="modal-content bed-file-options">
            <div className="modal-header">
              <h2>{t('bedFileModalTitle')}</h2>
              <button 
                className="btn-close" 
                onClick={() => {
                  setShowBedFileOptions(false);
                  setBedFileContent('');
                  setBedFileName('');
                  setUploadedFile(null);
                }}
              >
                ✕
              </button>
            </div>
            
            <div className="bed-file-content">
              <div className="file-upload-section">
                <h3>carregar arquivo .bed</h3>
                <input
                  type="file"
                  accept=".bed"
                  onChange={handleBedFileUpload}
                  className="file-input"
                />
                {uploadedFile && (
                  <p className="file-info">arquivo carregado: {uploadedFile.name}</p>
                )}
              </div>
              
              <div className="file-editor-section">
                <h3>{t('bedEditorSectionTitle')}</h3>
                <div className="editor-controls">
                  <button type="button" className="btn-load-template" onClick={() => void loadDefaultBedTemplate()}>
                    {t('bedEditorLoadTemplateBtn')}
                  </button>
                </div>
                <textarea
                  value={bedFileContent}
                  onChange={(e) => setBedFileContent(e.target.value)}
                  placeholder="cole aqui o conteúdo do arquivo .bed ou carregue um arquivo..."
                  className="bed-editor"
                  rows={15}
                />
              </div>
              
              <div className="file-actions">
                <button
                  type="button"
                  className="btn-process"
                  onClick={() => void processBedFile()}
                  disabled={!bedFileContent.trim()}
                >
                  {bedProcessActionLabel()}
                </button>
                <button 
                  className="btn-cancel"
                  onClick={() => {
                    setShowBedFileOptions(false);
                    setBedFileContent('');
                    setBedFileName('');
                    setUploadedFile(null);
                  }}
                >
                  cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    
      {/* header com progresso */}
      {step > 0 && (
        <div className="wizard-header">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${(step / (steps.length - 1)) * 100}%` }}
            ></div>
          </div>
          <div className="step-indicator">
            passo {step} de {steps.length - 1}: {steps[step].title}
          </div>
        </div>
      )}

      {/* conteúdo do wizard */}
      <div className="wizard-content">
        {step === 0 && renderModeSelection()}
        {step === 1 && renderBedSection()}
        {step === 2 && renderLidsSection()}
        {step === 3 && renderParticlesSection()}
        {step === 4 && renderPackingSection()}
        {step === 5 && renderExportSection()}
        {step === 6 && (
          <div className="form-section">
            <h2>parâmetros CFD (opcional)</h2>
            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={includeCFD}
                  onChange={(e) => setIncludeCFD(e.target.checked)}
                />
                incluir parâmetros de simulação CFD
              </label>
            </div>
            {includeCFD && (
              <p className="info-message">
                parâmetros CFD serão configurados na próxima etapa
              </p>
            )}
          </div>
        )}
        {step === 7 && renderConfirmation()}
      </div>

      {/* botões de navegação */}
      {step > 0 && (
        <div className="wizard-footer">
          <button 
            className="btn btn-secondary" 
            onClick={handlePrev}
          >
            ← voltar
          </button>
          
          {step < steps.length - 1 ? (
            <button className="btn btn-primary" onClick={handleNext}>
              próximo →
            </button>
          ) : (
            <button className="btn btn-success" onClick={handleSubmit}>
              gerar arquivo .bed
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default BedWizard;

