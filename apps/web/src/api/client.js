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

export async function fetchTeams() {
  const res = await fetch(`${API_URL}/teams`)
  const data = await handle(res, 'No se pudieron cargar los equipos')
  return data.teams || []
}
export async function fetchFixtures() {
  const res = await fetch(`${API_URL}/fixtures/today`)
  const data = await handle(res, 'No se pudieron cargar los partidos sugeridos')
  return data.fixtures || []
}
export async function fetchModelInfo() {
  const res = await fetch(`${API_URL}/model-info`)
  return handle(res, 'No se pudo cargar la información del modelo')
}
export async function predictMatch(payload) {
  const res = await fetch(`${API_URL}/predict`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
  return handle(res, 'No se pudo generar la predicción')
}
export async function compareMatches(matches) {
  const res = await fetch(`${API_URL}/compare`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({matches}) })
  return handle(res, 'No se pudieron comparar los partidos')
}
export async function fetchDatasetSummary() {
  const res = await fetch(`${API_URL}/admin/dataset-summary`)
  return handle(res, 'No se pudo cargar el resumen del dataset')
}
export async function fetchJobs() {
  const res = await fetch(`${API_URL}/admin/jobs`)
  return handle(res, 'No se pudieron cargar los jobs')
}
export async function uploadDatasets(formData) {
  const res = await fetch(`${API_URL}/admin/upload-results`, { method:'POST', body: formData })
  return handle(res, 'No se pudieron subir los archivos')
}
export async function addMatch(payload) {
  const res = await fetch(`${API_URL}/admin/add-match`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
  return handle(res, 'No se pudo guardar el partido')
}
export async function runAdminAction(action) {
  const res = await fetch(`${API_URL}/admin/${action}`, { method:'POST' })
  return handle(res, `No se pudo ejecutar ${action}`)
}
