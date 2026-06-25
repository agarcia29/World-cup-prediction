const API_URL = import.meta.env.VITE_API_URL || ''

async function handle(res, message) {
  if (!res.ok) {
    let detail = ''
    try {
      const data = await res.json()
      detail = data.detail || data.message || ''
    } catch {}
    throw new Error(detail || message)
  }
  return res.json()
}

const get = (path, msg) => fetch(`${API_URL}${path}`).then(res => handle(res, msg))
const post = (path, body, msg, isForm=false) => fetch(`${API_URL}${path}`, {
  method:'POST',
  headers: isForm ? undefined : {'Content-Type':'application/json'},
  body: isForm ? body : (body ? JSON.stringify(body) : undefined)
}).then(res => handle(res, msg))

export const fetchTeams = () => get('/teams', 'No se pudieron cargar los equipos').then(d => d.teams || [])
export const fetchFixtures = () => get('/fixtures/today', 'No se pudieron cargar los partidos sugeridos').then(d => d.fixtures || [])
export const fetchModelInfo = () => get('/model-info', 'No se pudo cargar la información del modelo')
export const predictMatch = (payload) => post('/predict', payload, 'No se pudo generar la predicción')
export const compareMatches = (matches) => post('/compare', {matches}, 'No se pudieron comparar los partidos')
export const fetchDatasetSummary = () => get('/admin/dataset-summary', 'No se pudo cargar el resumen del dataset')
export const fetchJobs = () => get('/admin/jobs', 'No se pudieron cargar los jobs')
export const fetchJob = (jobId) => get(`/admin/jobs/${jobId}`, 'No se pudo cargar el job')
export const fetchModelsSummary = () => get('/admin/models-summary', 'No se pudo cargar el resumen de modelos')
export const uploadDatasets = (formData) => post('/admin/upload-results', formData, 'No se pudieron subir los archivos', true)
export const uploadModelArtifact = (formData) => post('/admin/upload-model', formData, 'No se pudo subir el modelo', true)
export const addMatch = (payload) => post('/admin/add-match', payload, 'No se pudo guardar el partido')
export const runAdminAction = (action) => post(`/admin/${action}`, null, `No se pudo ejecutar ${action}`)