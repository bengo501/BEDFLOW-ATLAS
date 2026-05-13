import { useState, useEffect, useCallback } from 'react'
import {
  listModels3D,
  listSimulations,
  getSimulation,
  getSimulationResults,
  buildGeneratedFileUrl,
} from '../services/api'
import ModelViewer from './ModelViewer'
import ThemeIcon from './ThemeIcon'
import BackendConnectionError from './BackendConnectionError'
import PaginationControls from './PaginationControls'
import { useLanguage } from '../context/LanguageContext'
import { useActiveUser } from '../context/UserContext'

function ResultsList() {
  const { t, language } = useLanguage()
  const { activeUserId } = useActiveUser()
  const [models, setModels] = useState([])
  const [simulations, setSimulations] = useState([])
  const [selectedModel, setSelectedModel] = useState(null)
  const [selectedSimulation, setSelectedSimulation] = useState(null)
  const [selectedSimulationResults, setSelectedSimulationResults] = useState([])
  const [simulationResultsLoading, setSimulationResultsLoading] = useState(false)
  const [simulationResultsMeta, setSimulationResultsMeta] = useState({ page: 1, limit: 12, total: 0, total_pages: 1 })
  const [simulationResultsFilter, setSimulationResultsFilter] = useState({ resultType: '', search: '' })
  const [loading, setLoading] = useState(false)
  const [connectionError, setConnectionError] = useState(null)
  const [modelPage, setModelPage] = useState(1)
  const [modelLimit, setModelLimit] = useState(8)
  const [modelTotal, setModelTotal] = useState(0)
  const [modelTotalPages, setModelTotalPages] = useState(1)
  const [modelFilters, setModelFilters] = useState({
    search: '',
    packing_method: '',
    has_blend: '',
    has_stl: '',
  })
  const [simPage, setSimPage] = useState(1)
  const [simLimit, setSimLimit] = useState(8)
  const [simTotal, setSimTotal] = useState(0)
  const [simTotalPages, setSimTotalPages] = useState(1)
  const [simFilters, setSimFilters] = useState({
    search: '',
    status: '',
    regime: '',
  })

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      setConnectionError(null)
      const [modelsData, simsData] = await Promise.all([
        listModels3D({
          page: modelPage,
          limit: modelLimit,
          search: modelFilters.search,
          packing_method: modelFilters.packing_method || null,
          has_blend: modelFilters.has_blend === '' ? null : modelFilters.has_blend === 'true',
          has_stl: modelFilters.has_stl === '' ? null : modelFilters.has_stl === 'true',
        }),
        listSimulations({
          page: simPage,
          limit: simLimit,
          search: simFilters.search,
          status: simFilters.status || null,
          regime: simFilters.regime || null,
        }),
      ])
      setModels(Array.isArray(modelsData?.items) ? modelsData.items : [])
      setSimulations(Array.isArray(simsData?.items) ? simsData.items : [])
      setModelTotal(modelsData?.total || 0)
      setModelTotalPages(modelsData?.total_pages || modelsData?.pages || 1)
      setSimTotal(simsData?.total || 0)
      setSimTotalPages(simsData?.total_pages || simsData?.pages || 1)
    } catch (error) {
      console.error('erro ao carregar resultados reais:', error)
      setConnectionError(t('backendConnectionError'))
      setModels([])
      setSimulations([])
    } finally {
      setLoading(false)
    }
  }, [modelFilters, modelLimit, modelPage, simFilters, simLimit, simPage, t])

  useEffect(() => {
    loadData()
    const timer = window.setInterval(loadData, 5000)
    return () => window.clearInterval(timer)
  }, [activeUserId, loadData])

  const handleOpenSimulationResults = async (
    simulationId,
    options = {
      page: simulationResultsMeta.page,
      limit: simulationResultsMeta.limit,
      resultType: simulationResultsFilter.resultType,
      search: simulationResultsFilter.search,
    }
  ) => {
    try {
      setSimulationResultsLoading(true)
      const [sim, results] = await Promise.all([
        getSimulation(simulationId),
        getSimulationResults(simulationId, options),
      ])
      setSelectedSimulation(sim)
      setSelectedSimulationResults(Array.isArray(results?.items) ? results.items : [])
      setSimulationResultsMeta({
        page: results?.page || options.page || 1,
        limit: results?.limit || options.limit || 12,
        total: results?.total || 0,
        total_pages: results?.total_pages || results?.pages || 1,
      })
    } catch (error) {
      console.error('erro ao carregar resultados da simulação:', error)
      setConnectionError(t('backendConnectionError'))
    } finally {
      setSimulationResultsLoading(false)
    }
  }

  const handleDownloadSimulationJson = async (simulationId) => {
    try {
      const data = await getSimulation(simulationId)
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `simulacao_${simulationId}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (error) {
      console.error('erro ao baixar json da simulação:', error)
      setConnectionError(t('backendConnectionError'))
    }
  }

  const getModelPreviewPath = (model) => {
    return model.preview_model_url
      ? buildGeneratedFileUrl(model.preview_model_url.replace(/^\/files\//, ''))
      : buildGeneratedFileUrl(model.blend_file_path || model.stl_file_path)
  }

  const getModelDownloadPath = (model) => {
    return buildGeneratedFileUrl(model.blend_file_path || model.stl_file_path)
  }

  return (
    <div className="results-container">
      <header className="results-page-header">
        <div className="results-page-title">
          <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="" className="results-page-title-icon" />
          <h1 className="results-page-heading">{language === 'pt' ? 'Resultados' : 'Results'}</h1>
        </div>
      </header>

      {connectionError && <BackendConnectionError message={connectionError} />}

      <div className="results-layout">
        <section className="results-section">
          <h3>
            <ThemeIcon light="modelLight-removebg-preview.png" dark="modelDark-removebg-preview.png" alt="modelos" className="section-icon" />
            {language === 'pt' ? 'Modelos 3d' : '3d models'} ({modelTotal})
          </h3>

          <div className="results-filters">
            <input
              type="search"
              className="search-input"
              placeholder={language === 'pt' ? 'Buscar modelo…' : 'Search model…'}
              value={modelFilters.search}
              onChange={(e) => {
                setModelPage(1)
                setModelFilters((prev) => ({ ...prev, search: e.target.value }))
              }}
            />
            <select
              className="search-input"
              value={modelFilters.packing_method}
              onChange={(e) => {
                setModelPage(1)
                setModelFilters((prev) => ({ ...prev, packing_method: e.target.value }))
              }}
            >
              <option value="">{language === 'pt' ? 'Todos os métodos' : 'All methods'}</option>
              <option value="spherical_packing">spherical_packing</option>
              <option value="hexagonal_3d">hexagonal_3d</option>
              <option value="rigid_body">rigid_body</option>
            </select>
            <select
              className="search-input"
              value={modelFilters.has_blend}
              onChange={(e) => {
                setModelPage(1)
                setModelFilters((prev) => ({ ...prev, has_blend: e.target.value }))
              }}
            >
              <option value="">{language === 'pt' ? 'Blend: qualquer' : 'Blend: any'}</option>
              <option value="true">{language === 'pt' ? 'Com .blend' : 'With .blend'}</option>
              <option value="false">{language === 'pt' ? 'Sem .blend' : 'Without .blend'}</option>
            </select>
            <button
              className="btn-small"
              onClick={() => {
                setModelPage(1)
                setModelFilters({ search: '', packing_method: '', has_blend: '', has_stl: '' })
              }}
            >
              {language === 'pt' ? 'Limpar filtros' : 'Clear filters'}
            </button>
          </div>

          {loading ? (
            <p>{language === 'pt' ? 'Carregando…' : 'Loading…'}</p>
          ) : models.length === 0 ? (
            <p className="empty-state">{language === 'pt' ? 'Nenhum modelo encontrado' : 'No models found'}</p>
          ) : (
            <div className="files-grid">
              {models.map((model) => (
                <div key={model.id} className="file-card">
                  <div className="file-icon">
                    <ThemeIcon light="modelLight-removebg-preview.png" dark="modelDark-removebg-preview.png" alt="modelo" className="file-icon-img" />
                  </div>

                  <div className="file-info">
                    <h4 className="file-name">{model.name}</h4>
                    <p className="file-size">id {model.id}</p>
                    <p className="file-date">
                      {model.created_at
                        ? new Date(model.created_at).toLocaleDateString(language === 'pt' ? 'pt-BR' : 'en-US')
                        : '—'}
                    </p>
                    <p className="file-size">
                      {model.blend_file_path ? '.blend ' : ''}
                      {model.stl_file_path ? '.stl' : ''}
                    </p>
                  </div>

                  <div className="file-actions">
                    <button
                      className="btn-small"
                      onClick={() => setSelectedModel({ ...model, path: getModelPreviewPath(model) })}
                      disabled={!getModelPreviewPath(model)}
                    >
                      <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="visualizar" className="btn-icon" />
                      {language === 'pt' ? 'Visualizar' : 'View'}
                    </button>
                    <button
                      className="btn-small"
                      onClick={() => window.open(getModelDownloadPath(model), '_blank')}
                      disabled={!getModelDownloadPath(model)}
                    >
                      <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="baixar" className="btn-icon" />
                      {language === 'pt' ? 'Baixar' : 'Download'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
          <PaginationControls
            page={modelPage}
            totalPages={modelTotalPages}
            total={modelTotal}
            limit={modelLimit}
            loading={loading}
            onPageChange={setModelPage}
            onLimitChange={(value) => {
              setModelPage(1)
              setModelLimit(value)
            }}
            label={language === 'pt' ? 'Modelos 3d' : '3d models'}
            pt={language === 'pt'}
          />
        </section>

        <section className="results-section">
          <h3>
            <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="simulações" className="section-icon" />
            {language === 'pt' ? 'Simulações' : 'Simulations'} ({simTotal})
          </h3>

          <div className="results-filters">
            <input
              type="search"
              className="search-input"
              placeholder={language === 'pt' ? 'Buscar simulação…' : 'Search simulation…'}
              value={simFilters.search}
              onChange={(e) => {
                setSimPage(1)
                setSimFilters((prev) => ({ ...prev, search: e.target.value }))
              }}
            />
            <select
              className="search-input"
              value={simFilters.status}
              onChange={(e) => {
                setSimPage(1)
                setSimFilters((prev) => ({ ...prev, status: e.target.value }))
              }}
            >
              <option value="">{language === 'pt' ? 'Todos os estados' : 'All statuses'}</option>
              <option value="completed">{language === 'pt' ? 'Concluída' : 'Completed'}</option>
              <option value="running">{language === 'pt' ? 'Em execução' : 'Running'}</option>
              <option value="pending">{language === 'pt' ? 'Pendente' : 'Pending'}</option>
              <option value="failed">{language === 'pt' ? 'Falhou' : 'Failed'}</option>
            </select>
            <select
              className="search-input"
              value={simFilters.regime}
              onChange={(e) => {
                setSimPage(1)
                setSimFilters((prev) => ({ ...prev, regime: e.target.value }))
              }}
            >
              <option value="">{language === 'pt' ? 'Todos os regimes' : 'All regimes'}</option>
              <option value="laminar">laminar</option>
              <option value="turbulent">turbulent</option>
            </select>
            <button
              className="btn-small"
              onClick={() => {
                setSimPage(1)
                setSimFilters({ search: '', status: '', regime: '' })
              }}
            >
              {language === 'pt' ? 'Limpar filtros' : 'Clear filters'}
            </button>
          </div>

          {loading ? (
            <p>{language === 'pt' ? 'Carregando…' : 'Loading…'}</p>
          ) : simulations.length === 0 ? (
            <p className="empty-state">{language === 'pt' ? 'Nenhuma simulação encontrada' : 'No simulations found'}</p>
          ) : (
            <div className="files-grid">
              {simulations.map((sim) => (
                <div key={sim.id} className="file-card">
                  <div className="file-icon">
                    <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="simulação" className="file-icon-img" />
                  </div>

                  <div className="file-info">
                    <h4 className="file-name">{sim.name}</h4>
                    <p className="file-size">id {sim.id}</p>
                    <p className="file-date">
                      {sim.created_at
                        ? new Date(sim.created_at).toLocaleDateString(language === 'pt' ? 'pt-BR' : 'en-US')
                        : '—'}
                    </p>
                    <p className="file-size">{sim.status}</p>
                  </div>

                  <div className="file-actions">
                    <button
                      className="btn-small"
                      onClick={() => {
                        setSimulationResultsFilter({ resultType: '', search: '' })
                        setSimulationResultsMeta({ page: 1, limit: 12, total: 0, total_pages: 1 })
                        handleOpenSimulationResults(sim.id, { page: 1, limit: 12 })
                      }}
                    >
                      <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="resultados" className="btn-icon" />
                      {language === 'pt' ? 'Resultados' : 'Results'}
                    </button>
                    <button
                      className="btn-small"
                      onClick={() => handleDownloadSimulationJson(sim.id)}
                    >
                      <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="baixar" className="btn-icon" />
                      json
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
          <PaginationControls
            page={simPage}
            totalPages={simTotalPages}
            total={simTotal}
            limit={simLimit}
            loading={loading}
            onPageChange={setSimPage}
            onLimitChange={(value) => {
              setSimPage(1)
              setSimLimit(value)
            }}
            label={language === 'pt' ? 'Simulações' : 'Simulations'}
            pt={language === 'pt'}
          />
        </section>
      </div>

      {selectedModel && (
        <div className="modal-overlay" onClick={() => setSelectedModel(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="modal-close"
              onClick={() => setSelectedModel(null)}
            >
              x
            </button>

            <h3>{language === 'pt' ? 'Visualização 3d' : '3d preview'}: {selectedModel.name}</h3>

            <ModelViewer modelPath={selectedModel.path} />
          </div>
        </div>
      )}

      {selectedSimulation && (
        <div className="modal-overlay" onClick={() => setSelectedSimulation(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="modal-close"
              onClick={() => setSelectedSimulation(null)}
            >
              x
            </button>

            <h3>{language === 'pt' ? 'Resultados da simulação' : 'Simulation results'}: {selectedSimulation.name}</h3>

            {simulationResultsLoading ? (
              <p>{language === 'pt' ? 'Carregando…' : 'Loading…'}</p>
            ) : selectedSimulationResults.length === 0 ? (
              <p>{language === 'pt' ? 'Nenhum resultado persistido para esta simulação' : 'No persisted results for this simulation'}</p>
            ) : (
              <>
                <div className="results-filters">
                  <input
                    type="search"
                    className="search-input"
                    placeholder={language === 'pt' ? 'Buscar resultado…' : 'Search result…'}
                    value={simulationResultsFilter.search}
                    onChange={(e) => setSimulationResultsFilter((prev) => ({ ...prev, search: e.target.value }))}
                  />
                  <select
                    className="search-input"
                    value={simulationResultsFilter.resultType}
                    onChange={(e) => setSimulationResultsFilter((prev) => ({ ...prev, resultType: e.target.value }))}
                  >
                    <option value="">{language === 'pt' ? 'Todos os tipos' : 'All types'}</option>
                    <option value="field">field</option>
                    <option value="metric">metric</option>
                    <option value="validation">validation</option>
                    <option value="visualization">visualization</option>
                  </select>
                  <button
                    className="btn-small"
                    onClick={() =>
                      handleOpenSimulationResults(selectedSimulation.id, {
                        page: 1,
                        limit: simulationResultsMeta.limit,
                        resultType: simulationResultsFilter.resultType || null,
                        search: simulationResultsFilter.search || null,
                      })
                    }
                  >
                    {language === 'pt' ? 'Aplicar filtros' : 'Apply filters'}
                  </button>
                </div>
                <div className="files-grid">
                  {selectedSimulationResults.map((result) => (
                    <div key={result.id} className="file-card">
                      <div className="file-info">
                        <h4 className="file-name">{result.name}</h4>
                        <p className="file-size">{result.result_type}</p>
                        <p className="file-date">
                          {result.value != null ? `${result.value} ${result.unit || ''}`.trim() : (language === 'pt' ? 'Sem valor escalar' : 'No scalar value')}
                        </p>
                        <p className="file-size">{result.file_type || 'json'}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <PaginationControls
                  page={simulationResultsMeta.page}
                  totalPages={simulationResultsMeta.total_pages}
                  total={simulationResultsMeta.total}
                  limit={simulationResultsMeta.limit}
                  loading={simulationResultsLoading}
                  onPageChange={(page) =>
                    handleOpenSimulationResults(selectedSimulation.id, {
                      page,
                      limit: simulationResultsMeta.limit,
                      resultType: simulationResultsFilter.resultType || null,
                      search: simulationResultsFilter.search || null,
                    })
                  }
                  onLimitChange={(value) =>
                    handleOpenSimulationResults(selectedSimulation.id, {
                      page: 1,
                      limit: value,
                      resultType: simulationResultsFilter.resultType || null,
                      search: simulationResultsFilter.search || null,
                    })
                  }
                  label={language === 'pt' ? 'Resultados persistidos' : 'Persisted results'}
                  pt={language === 'pt'}
                />
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ResultsList

