import { useEffect, useState } from 'react'

const API_URL = 'http://127.0.0.1:8000'

const DOCUMENT_TYPES = [
  { value: 'price_sheet', label: 'Preisblatt' },
  { value: 'agb', label: 'AGB' },
  { value: 'power_of_attorney', label: 'Vollmacht' },
  { value: 'form', label: 'Formular' },
  { value: 'other', label: 'Sonstiges' },
]

function Documents() {
  const [tariffs, setTariffs] = useState([])
  const [selectedTariffId, setSelectedTariffId] = useState('')
  const [documentType, setDocumentType] = useState('form')
  const [file, setFile] = useState(null)
  const [documents, setDocuments] = useState([])

  const [loadingTariffs, setLoadingTariffs] = useState(true)
  const [loadingDocuments, setLoadingDocuments] = useState(false)
  const [uploading, setUploading] = useState(false)

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const token = localStorage.getItem('access_token')

  useEffect(() => {
    async function loadTariffs() {
      setLoadingTariffs(true)
      setError('')

      try {
        const response = await fetch(`${API_URL}/tariffs`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            data.detail || 'Tarife konnten nicht geladen werden.'
          )
        }

        setTariffs(data)

        if (data.length > 0) {
          setSelectedTariffId(String(data[0].id))
        }
      } catch (err) {
        setError(
          err.message || 'Tarife konnten nicht geladen werden.'
        )
      } finally {
        setLoadingTariffs(false)
      }
    }

    loadTariffs()
  }, [token])

  useEffect(() => {
    if (!selectedTariffId) {
      setDocuments([])
      return
    }

    loadDocuments(selectedTariffId)
  }, [selectedTariffId])

  async function loadDocuments(tariffId) {
    setLoadingDocuments(true)
    setError('')

    try {
      const response = await fetch(
        `${API_URL}/tariff-documents/tariffs/${tariffId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Dokumente konnten nicht geladen werden.'
        )
      }

      setDocuments(data)
    } catch (err) {
      setDocuments([])
      setError(
        err.message || 'Dokumente konnten nicht geladen werden.'
      )
    } finally {
      setLoadingDocuments(false)
    }
  }

  async function handleUpload(event) {
    event.preventDefault()

    if (!selectedTariffId) {
      setError('Bitte wählen Sie einen Tarif aus.')
      return
    }

    if (!file) {
      setError('Bitte wählen Sie eine PDF-Datei aus.')
      return
    }

    setUploading(true)
    setError('')
    setSuccess('')

    try {
      const formData = new FormData()
      formData.append('document_type', documentType)
      formData.append('file', file)

      const response = await fetch(
        `${API_URL}/tariff-documents/tariffs/${selectedTariffId}`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'PDF konnte nicht hochgeladen werden.'
        )
      }

      setFile(null)
      setSuccess('PDF wurde erfolgreich hochgeladen.')

      const fileInput = document.getElementById('tariff-pdf-file')
      if (fileInput) {
        fileInput.value = ''
      }

      await loadDocuments(selectedTariffId)
    } catch (err) {
      setError(
        err.message || 'PDF konnte nicht hochgeladen werden.'
      )
    } finally {
      setUploading(false)
    }
  }

  async function openDocument(documentItem) {
    setError('')

    try {
      const response = await fetch(
        `${API_URL}${documentItem.download_url}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        let message = 'PDF konnte nicht geöffnet werden.'

        try {
          const data = await response.json()
          message = data.detail || message
        } catch {
          // File response / non-JSON error
        }

        throw new Error(message)
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)

      window.open(url, '_blank', 'noopener,noreferrer')

      window.setTimeout(() => {
        URL.revokeObjectURL(url)
      }, 60000)
    } catch (err) {
      setError(
        err.message || 'PDF konnte nicht geöffnet werden.'
      )
    }
  }

  function getDocumentTypeLabel(value) {
    return (
      DOCUMENT_TYPES.find((item) => item.value === value)?.label ||
      value
    )
  }

  const selectedTariff = tariffs.find(
    (tariff) => String(tariff.id) === selectedTariffId
  )

  return (
    <div className="page-content">
      <div className="documents-page">
        <div className="documents-page-header">
          <div>
            <h1>Dokumente</h1>
            <p>
              PDF-Dokumente für Tarife verwalten und bereitstellen.
            </p>
          </div>
        </div>

        {error && (
          <div className="documents-message documents-message-error">
            {error}
          </div>
        )}

        {success && (
          <div className="documents-message documents-message-success">
            {success}
          </div>
        )}

        <div className="documents-grid">
          <section className="documents-card">
            <div className="documents-card-header">
              <div>
                <span className="documents-eyebrow">
                  Tarifdokument
                </span>
                <h2>PDF hochladen</h2>
              </div>

              <span className="documents-pdf-badge">PDF</span>
            </div>

            <form
              className="documents-upload-form"
              onSubmit={handleUpload}
            >
              <label>
                Tarif
                <select
                  value={selectedTariffId}
                  onChange={(event) => {
                    setSelectedTariffId(event.target.value)
                    setSuccess('')
                  }}
                  disabled={loadingTariffs}
                  required
                >
                  {loadingTariffs && (
                    <option value="">Tarife werden geladen...</option>
                  )}

                  {!loadingTariffs && tariffs.length === 0 && (
                    <option value="">Keine Tarife vorhanden</option>
                  )}

                  {tariffs.map((tariff) => (
                    <option
                      key={tariff.id}
                      value={tariff.id}
                    >
                      {tariff.name}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Dokumenttyp
                <select
                  value={documentType}
                  onChange={(event) =>
                    setDocumentType(event.target.value)
                  }
                >
                  {DOCUMENT_TYPES.map((type) => (
                    <option
                      key={type.value}
                      value={type.value}
                    >
                      {type.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="documents-file-field">
                PDF-Datei
                <input
                  id="tariff-pdf-file"
                  type="file"
                  accept="application/pdf,.pdf"
                  onChange={(event) =>
                    setFile(event.target.files?.[0] || null)
                  }
                  required
                />
              </label>

              {file && (
                <div className="documents-selected-file">
                  <span>PDF</span>
                  <div>
                    <strong>{file.name}</strong>
                    <small>
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </small>
                  </div>
                </div>
              )}

              <button
                type="submit"
                className="documents-upload-button"
                disabled={
                  uploading ||
                  !selectedTariffId ||
                  !file
                }
              >
                {uploading
                  ? 'PDF wird hochgeladen...'
                  : 'PDF hochladen'}
              </button>

              <small className="documents-upload-hint">
                Nur PDF-Dateien, maximal 10 MB.
              </small>
            </form>
          </section>

          <section className="documents-card">
            <div className="documents-card-header">
              <div>
                <span className="documents-eyebrow">
                  Hinterlegte Dateien
                </span>

                <h2>
                  {selectedTariff?.name || 'Tarif auswählen'}
                </h2>
              </div>

              <span className="documents-count">
                {documents.length}
              </span>
            </div>

            {loadingDocuments ? (
              <div className="documents-empty">
                Dokumente werden geladen...
              </div>
            ) : documents.length === 0 ? (
              <div className="documents-empty">
                <strong>Noch keine PDF-Dokumente</strong>
                <span>
                  Laden Sie links das erste Dokument für diesen
                  Tarif hoch.
                </span>
              </div>
            ) : (
              <div className="documents-list">
                {documents.map((documentItem) => (
                  <button
                    type="button"
                    className="documents-list-item"
                    key={documentItem.id}
                    onClick={() => openDocument(documentItem)}
                  >
                    <span className="documents-file-icon">
                      PDF
                    </span>

                    <span className="documents-file-info">
                      <strong>
                        {getDocumentTypeLabel(
                          documentItem.document_type
                        )}
                      </strong>

                      <span>{documentItem.file_name}</span>
                    </span>

                    <span className="documents-open">
                      Öffnen →
                    </span>
                  </button>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}

export default Documents
