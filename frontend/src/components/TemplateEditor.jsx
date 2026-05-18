import { useState, useEffect } from 'react'
import { useLanguage } from '../context/LanguageContext'
import ThemeIcon from './ThemeIcon'
import BackendConnectionError from './BackendConnectionError'
import '../styles/TemplateEditor.css'
import {
  getBedTemplateDefault,
  listTemplates,
  saveTemplate,
  getTemplate,
  deleteTemplate,
} from '../services/api'

function IconCopy({ className }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  )
}

function IconDownload({ className }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  )
}

function TemplateEditor() {
  const { language, t } = useLanguage()
  const pt = language === 'pt'
  const [bedContent, setBedContent] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [savedTemplates, setSavedTemplates] = useState([])
  const [showTemplateManager, setShowTemplateManager] = useState(false)
  const [connectionError, setConnectionError] = useState(null)

  useEffect(() => {
    setConnectionError(null)
    loadDefaultTemplate()
    loadSavedTemplates()
  }, [])

  const loadDefaultTemplate = async () => {
    try {
      setIsLoading(true)
      const data = await getBedTemplateDefault()
      setBedContent(data.content)
    } catch (error) {
      console.error('erro ao carregar template padrão:', error)
      setConnectionError(t('backendConnectionError'))
    } finally {
      setIsLoading(false)
    }
  }

  const loadSavedTemplates = async () => {
    try {
      const data = await listTemplates({ page: 1, limit: 100 })
      setSavedTemplates(Array.isArray(data) ? data : data.items || data.templates || [])
    } catch (error) {
      console.error('erro ao carregar templates salvos:', error)
      setConnectionError(t('backendConnectionError'))
    }
  }

  const handleGenerateFromForm = async () => {
    setConnectionError(null)
    // aqui você pode implementar a lógica para gerar baseado nos parâmetros do formulário
    // por enquanto, vamos usar o template padrão
    await loadDefaultTemplate()
  }

  const handleImportFile = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setBedContent(e.target.result)
      }
      reader.readAsText(file)
    }
  }

  const handleCopyContent = () => {
    navigator.clipboard.writeText(bedContent)
    alert('conteúdo copiado para a área de transferência!')
  }

  const handleDownloadFile = () => {
    const blob = new Blob([bedContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'template.bed'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleSaveTemplate = async () => {
    const templateName = prompt('nome do template:')
    if (templateName) {
      try {
        setConnectionError(null)
        await saveTemplate({
          name: templateName,
          content: bedContent
        })
        alert('template salvo com sucesso!')
        loadSavedTemplates()
      } catch (error) {
        console.error('erro ao salvar template:', error)
        setConnectionError(t('backendConnectionError'))
      }
    }
  }

  const handleLoadTemplate = async (templateId) => {
    try {
      setConnectionError(null)
      const data = await getTemplate(templateId)
      setBedContent(data.content)
      setShowTemplateManager(false)
    } catch (error) {
      console.error('erro ao carregar template:', error)
      setConnectionError(t('backendConnectionError'))
    }
  }

  const handleDeleteTemplate = async (templateId) => {
    if (confirm('tem certeza que deseja excluir este template?')) {
      try {
        setConnectionError(null)
        await deleteTemplate(templateId)
        alert('template excluído com sucesso!')
        loadSavedTemplates()
      } catch (error) {
        console.error('erro ao excluir template:', error)
        setConnectionError(t('backendConnectionError'))
      }
    }
  }

  const handleCreateAndExecute = () => {
    // aqui você pode implementar a lógica para criar e executar o pipeline
    alert('funcionalidade de criar e executar será implementada aqui!')
  }

  return (
    <div className="template-editor-container">
      <div className="template-editor-header">
        <h2>{pt ? 'Arquivo .bed' : '.bed file'}</h2>
      </div>

      {connectionError && <BackendConnectionError message={connectionError} />}

      <div className="template-editor-actions">
        <button 
          className="btn-generate" 
          onClick={handleGenerateFromForm}
          disabled={isLoading}
        >
          <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="" className="btn-icon" location="page" />
          {pt ? 'Gerar automaticamente' : 'Generate automatically'}
          <span className="btn-subtitle">
            {pt ? 'Baseado nos parâmetros do formulário' : 'Based on form parameters'}
          </span>
        </button>

        <label className="btn-import">
          <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="" className="btn-icon" location="page" />
          {pt ? 'Importar arquivo' : 'Import file'}
          <span className="btn-subtitle">
            {pt ? 'Carregar arquivo .bed existente' : 'Load an existing .bed file'}
          </span>
          <input 
            type="file" 
            accept=".bed" 
            onChange={handleImportFile}
            style={{ display: 'none' }}
          />
        </label>
      </div>

      <div className="template-editor-content">
        <div className="content-header">
          <h3>{pt ? 'Conteúdo do arquivo .bed' : '.bed file contents'}</h3>
          <div className="content-actions">
            <button type="button" className="btn-copy" onClick={handleCopyContent}>
              <IconCopy className="template-toolbar-svg" />
              {pt ? 'Copiar' : 'Copy'}
            </button>
            <button type="button" className="btn-download" onClick={handleDownloadFile}>
              <IconDownload className="template-toolbar-svg" />
              {pt ? 'Baixar' : 'Download'}
            </button>
          </div>
        </div>

        <div className="bed-editor">
          <textarea
            value={bedContent}
            onChange={(e) => setBedContent(e.target.value)}
            placeholder={pt ? 'Conteúdo do arquivo .bed…' : '.bed file contents…'}
            className="bed-textarea"
          />
        </div>

        <div className="template-editor-hint">
          <p>
            {pt
              ? 'Este arquivo .bed é gerado automaticamente com base nos parâmetros do formulário. Pode editá-lo manualmente se necessário.'
              : 'This .bed file is generated automatically from the form parameters. You can edit it manually if needed.'}
          </p>
        </div>

        <div className="template-editor-inner-footer">
          <button type="button" className="btn-cancel">
            {pt ? 'Cancelar' : 'Cancel'}
          </button>
          <button type="button" className="btn-execute" onClick={handleCreateAndExecute}>
            <ThemeIcon
              light="playLight.png"
              dark="playLight.png"
              alt=""
              className="btn-icon btn-icon--on-primary"
              location="sidebar"
            />
            {pt ? 'Criar e executar' : 'Create and run'}
          </button>
        </div>
      </div>

      {/* modal para gerenciar templates */}
      {showTemplateManager && (
        <div className="template-manager-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>gerenciar templates</h3>
              <button 
                className="btn-close" 
                onClick={() => setShowTemplateManager(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              {savedTemplates.length === 0 ? (
                <p className="no-templates">nenhum template salvo</p>
              ) : (
                <div className="template-list">
                  {savedTemplates.map((template) => (
                    <div key={template.id} className="template-item">
                      <div className="template-info">
                        <h4>{template.name}</h4>
                        <p>criado em: {new Date(template.created_at).toLocaleDateString()}</p>
                      </div>
                      <div className="template-actions">
                        <button 
                          className="btn-load" 
                          onClick={() => handleLoadTemplate(template.id)}
                        >
                          carregar
                        </button>
                        <button 
                          className="btn-delete" 
                          onClick={() => handleDeleteTemplate(template.id)}
                        >
                          excluir
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TemplateEditor
