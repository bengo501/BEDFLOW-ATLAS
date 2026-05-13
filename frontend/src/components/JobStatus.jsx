import { useState, useEffect } from 'react'
import { listJobs } from '../services/api'
import ThemeIcon from './ThemeIcon'
import BackendConnectionError from './BackendConnectionError'
import { useLanguage } from '../context/LanguageContext'

function JobStatus({ currentJob }) {
  const { t, language } = useLanguage()
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [loading, setLoading] = useState(false)
  const [connectionError, setConnectionError] = useState(null)

  useEffect(() => {
    loadJobs()
    const sec = parseInt(localStorage.getItem('jobsPollIntervalSec'), 10)
    const pollSec = Number.isFinite(sec) && sec >= 3 && sec <= 120 ? sec : 5
    const interval = setInterval(loadJobs, pollSec * 1000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (currentJob) {
      setSelectedJob(currentJob)
    }
  }, [currentJob])

  const loadJobs = async () => {
    try {
      const jobsList = await listJobs()
      setJobs(jobsList)
      setConnectionError(null)

      // atualizar job selecionado se existir
      if (selectedJob) {
        const updated = jobsList.find(j => j.job_id === selectedJob.job_id)
        if (updated) {
          setSelectedJob(updated)
        }
      }
    } catch (error) {
      console.error('erro ao carregar jobs:', error)
      setConnectionError(t('backendConnectionError'))
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'queued': return '⏳'
      case 'running': return '🔄'
      case 'completed': return '✅'
      case 'failed': return '❌'
      default: return '❔'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'queued': return 'status-queued'
      case 'running': return 'status-running'
      case 'completed': return 'status-completed'
      case 'failed': return 'status-failed'
      default: return ''
    }
  }

  const getJobTypeLabel = (jobType) => {
    const pt = language === 'pt'
    switch (jobType) {
      case 'compile':
        return (
          <>
            <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="compilação" className="status-icon" />
            {pt ? 'Compilação' : 'Compile'}
          </>
        )
      case 'generate_model':
        return pt ? 'Modelo 3d' : '3d model'
      case 'simulation':
        return pt ? 'Simulação' : 'Simulation'
      case 'full_pipeline':
        return pt ? 'Pipeline completo' : 'Full pipeline'
      default:
        return jobType
    }
  }

  const dateLocale = language === 'pt' ? 'pt-BR' : 'en-US'

  return (
    <div className="job-status-container">
      <header className="jobs-page-header">
        <div className="jobs-page-title">
          <ThemeIcon light="job_monitor_clock_white.png" dark="job_monitor_clock_white.png" alt="" className="jobs-page-title-icon" />
          <h1 className="jobs-page-heading">{language === 'pt' ? 'Monitoramento de jobs' : 'Job monitoring'}</h1>
        </div>
      </header>

      {connectionError && <BackendConnectionError message={connectionError} />}

      <div className="jobs-layout">
        {/* lista de jobs */}
        <div className="jobs-list">
          <h3>{language === 'pt' ? `Todos os jobs (${jobs.length})` : `All jobs (${jobs.length})`}</h3>

          {jobs.length === 0 ? (
            <p className="empty-state">{language === 'pt' ? 'Nenhum job encontrado' : 'No jobs found'}</p>
          ) : (
            <div className="jobs-items">
              {jobs.map(job => (
                <div
                  key={job.job_id}
                  className={`job-item ${selectedJob?.job_id === job.job_id ? 'selected' : ''}`}
                  onClick={() => setSelectedJob(job)}
                >
                  <div className="job-header">
                    <span className="job-icon">{getStatusIcon(job.status)}</span>
                    <span className="job-type">{getJobTypeLabel(job.job_type)}</span>
                  </div>

                  <div className={`job-status ${getStatusColor(job.status)}`}>
                    {job.status}
                  </div>

                  <div className="job-progress">
                    <div
                      className="progress-bar"
                      style={{ width: `${job.progress}%` }}
                    />
                    <span className="progress-text">{job.progress}%</span>
                  </div>

                  <div className="job-time">
                    {new Date(job.created_at).toLocaleString(dateLocale)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* detalhes do job selecionado */}
        <div className="job-details">
          {selectedJob ? (
            <>
              <h3>{language === 'pt' ? 'Detalhes do job' : 'Job details'}</h3>

              <div className="detail-group">
                <label>{language === 'pt' ? 'Id:' : 'Id:'}</label>
                <code>{selectedJob.job_id}</code>
              </div>

              <div className="detail-group">
                <label>{language === 'pt' ? 'Tipo:' : 'Type:'}</label>
                <span>{getJobTypeLabel(selectedJob.job_type)}</span>
              </div>

              <div className="detail-group">
                <label>{language === 'pt' ? 'Status:' : 'Status:'}</label>
                <span className={`badge ${getStatusColor(selectedJob.status)}`}>
                  {getStatusIcon(selectedJob.status)} {selectedJob.status}
                </span>
              </div>

              <div className="detail-group">
                <label>{language === 'pt' ? 'Progresso:' : 'Progress:'}</label>
                <div className="progress-bar-large">
                  <div
                    className="progress-fill"
                    style={{ width: `${selectedJob.progress}%` }}
                  />
                  <span className="progress-label">{selectedJob.progress}%</span>
                </div>
              </div>

              <div className="detail-group">
                <label>{language === 'pt' ? 'Criado em:' : 'Created:'}</label>
                <span>{new Date(selectedJob.created_at).toLocaleString(dateLocale)}</span>
              </div>

              <div className="detail-group">
                <label>{language === 'pt' ? 'Atualizado em:' : 'Updated:'}</label>
                <span>{new Date(selectedJob.updated_at).toLocaleString(dateLocale)}</span>
              </div>

              {selectedJob.output_files && selectedJob.output_files.length > 0 && (
                <div className="detail-group">
                  <label>{language === 'pt' ? 'Arquivos gerados:' : 'Output files:'}</label>
                  <ul className="output-files">
                    {selectedJob.output_files.map((file, idx) => (
                      <li key={idx}>
                        <code>{file}</code>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedJob.error_message && (
                <div className="detail-group">
                  <label>{language === 'pt' ? 'Erro:' : 'Error:'}</label>
                  <div className="error-message">
                    {selectedJob.error_message}
                  </div>
                </div>
              )}

              {selectedJob.metadata && Object.keys(selectedJob.metadata).length > 0 && (
                <div className="detail-group">
                  <label>metadata:</label>
                  <pre className="metadata">
                    {JSON.stringify(selectedJob.metadata, null, 2)}
                  </pre>
                </div>
              )}
            </>
          ) : (
            <p className="empty-state">{language === 'pt' ? 'Selecione um job para ver detalhes' : 'Select a job to see details'}</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default JobStatus

