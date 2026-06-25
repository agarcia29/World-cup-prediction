import React, { useEffect, useMemo, useState } from 'react'
import { addMatch, fetchDatasetSummary, fetchJobs, fetchModelsSummary, runAdminAction, uploadDatasets, uploadModelArtifact } from '../api/client'

const initialMatch = { date:'2026-06-24', home_team:'Brazil', away_team:'France', home_score:2, away_score:1, tournament:'Friendly', city:'Miami', country:'United States', neutral:true }
const modelSlots = [
  ['xgb_home', 'xgb_home.pkl'],
  ['xgb_away', 'xgb_away.pkl'],
  ['feature_columns', 'feature_columns.json'],
  ['bayes_baseline', 'bayes_baseline.json'],
  ['bayes_pymc', 'bayes_pymc.nc'],
  ['team_index', 'team_index.json'],
]

export default function AdminPage() {
  const [summary, setSummary] = useState(null)
  const [jobs, setJobs] = useState([])
  const [models, setModels] = useState({})
  const [files, setFiles] = useState({})
  const [match, setMatch] = useState(initialMatch)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [modelSlot, setModelSlot] = useState('xgb_home')
  const [modelFile, setModelFile] = useState(null)

  async function load() {
    try {
      const [sum, jobsData, modelData] = await Promise.all([fetchDatasetSummary(), fetchJobs(), fetchModelsSummary()])
      setSummary(sum)
      setJobs(jobsData.jobs || [])
      setModels(modelData.models || {})
    } catch (e) { setError(e.message) }
  }
  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t) }, [])

  async function handleUpload(e) {
    e.preventDefault(); setBusy(true); setError(''); setMessage('')
    try {
      const fd = new FormData()
      if (files.results) fd.append('results', files.results)
      if (files.goalscorers) fd.append('goalscorers', files.goalscorers)
      if (files.shootouts) fd.append('shootouts', files.shootouts)
      const res = await uploadDatasets(fd)
      setMessage(`Archivos cargados: ${res.uploaded?.length || 0}`)
      await load()
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  async function handleModelUpload(e) {
    e.preventDefault(); setBusy(true); setError(''); setMessage('')
    try {
      if (!modelFile) throw new Error('Selecciona un archivo de modelo')
      const fd = new FormData()
      fd.append('slot', modelSlot)
      fd.append('model_file', modelFile)
      const res = await uploadModelArtifact(fd)
      setMessage(`Modelo cargado: ${res.filename}`)
      setModelFile(null)
      await load()
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  async function handleAddMatch(e) {
    e.preventDefault(); setBusy(true); setError(''); setMessage('')
    try { await addMatch(match); setMessage('Partido agregado al results.csv'); await load() } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  async function action(name) {
    setBusy(true); setError(''); setMessage('')
    try { const res = await runAdminAction(name); setMessage(`Job ${res.job_type || name}: ${res.status}`); await load() } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  const activeJobs = useMemo(() => jobs.filter(j => ['queued','running'].includes(j.status)).length, [jobs])

  return <div className="stack">
    <section className="card">
      <div className="section-head">
        <div><h3>Resumen del dataset</h3><p>Estado actual de archivos crudos, features y equipos.</p></div>
        <button className="secondary" onClick={load}>Refrescar</button>
      </div>
      <div className="summary-grid">
        {summary && Object.entries(summary).map(([key, val]) => (
          <div className="mini-stat" key={key}>
            <span>{key}</span>
            <strong>{val.exists === false ? 'No existe' : (val.rows ?? val.count ?? 0)}</strong>
            <small>{val.max_date || ''}</small>
          </div>
        ))}
      </div>
    </section>

    <section className="card">
      <div className="section-head"><div><h3>Subir dataset</h3><p>Sube uno o varios CSV para reemplazar los archivos de <code>data/raw</code>.</p></div></div>
      <form className="form-grid admin-upload" onSubmit={handleUpload}>
        <label>results.csv<input type="file" accept=".csv" onChange={e=>setFiles(f=>({...f, results:e.target.files?.[0]}))} /></label>
        <label>goalscorers.csv<input type="file" accept=".csv" onChange={e=>setFiles(f=>({...f, goalscorers:e.target.files?.[0]}))} /></label>
        <label>shootouts.csv<input type="file" accept=".csv" onChange={e=>setFiles(f=>({...f, shootouts:e.target.files?.[0]}))} /></label>
        <button className="primary" disabled={busy}>Subir archivos</button>
      </form>
    </section>

    <section className="card">
      <div className="section-head"><div><h3>Model Upload</h3><p>Sube modelos entrenados localmente para usarlos en Render sin reentrenar allá.</p></div></div>
      <form className="form-grid admin-upload" onSubmit={handleModelUpload}>
        <label>Slot del modelo
          <select value={modelSlot} onChange={e => setModelSlot(e.target.value)}>
            {modelSlots.map(([value, label]) => <option key={value} value={value}>{value} → {label}</option>)}
          </select>
        </label>
        <label>Archivo
          <input type="file" onChange={e => setModelFile(e.target.files?.[0] || null)} />
        </label>
        <button className="primary" disabled={busy}>Subir modelo</button>
      </form>
      <div className="summary-grid">
        {Object.entries(models).map(([key, val]) => (
          <div className="mini-stat" key={key}>
            <span>{key}</span>
            <strong>{val.exists ? 'Disponible' : 'Falta'}</strong>
            <small>{val.updated_at ? val.updated_at.slice(0, 19).replace('T', ' ') : val.filename}</small>
          </div>
        ))}
      </div>
    </section>

    <section className="card">
      <div className="section-head"><div><h3>Agregar partido manualmente</h3><p>Útil para alimentar un resultado nuevo sin reemplazar el CSV completo.</p></div></div>
      <form className="form-grid admin-match" onSubmit={handleAddMatch}>
        {Object.entries(match).map(([k,v]) => k==='neutral'
          ? <label key={k} className="checkbox"><input type="checkbox" checked={v} onChange={e=>setMatch(m=>({...m, neutral:e.target.checked}))}/>Neutral</label>
          : <label key={k}>{k}<input value={v} onChange={e=>setMatch(m=>({...m,[k]: ['home_score','away_score'].includes(k) ? Number(e.target.value) : e.target.value}))} /></label>)}
        <button className="primary" disabled={busy}>Guardar partido</button>
      </form>
    </section>

    <section className="card">
      <div className="section-head"><div><h3>Acciones de mantenimiento</h3><p>Jobs asíncronos para recalcular features y reentrenar XGBoost. Bayes pesado queda fuera de producción.</p></div></div>
      <div className="actions-grid">
        <button className="secondary" disabled={busy} onClick={() => action('rebuild-features')}>Recalcular features</button>
        <button className="secondary" disabled={busy} onClick={() => action('retrain-xgb')}>Reentrenar XGBoost</button>
        <button className="secondary" disabled={busy} onClick={() => action('retrain-bayes')}>Reentrenar Bayes baseline</button>
        <button className="secondary" disabled={busy} onClick={() => action('refresh-teams')}>Actualizar equipos</button>
      </div>
      <p className="muted">Jobs activos: <strong>{activeJobs}</strong>. El botón de Bayes pesado se desactiva en producción y la idea es entrenarlo localmente para luego subir el artefacto.</p>
      {message && <p>{message}</p>}
      {error && <p className="error">{error}</p>}
    </section>

    <section className="card">
      <div className="section-head"><div><h3>Historial de jobs</h3><p>Estado real de tareas de rebuild / XGB / refresh.</p></div></div>
      <div className="table-scroll">
        <table className="jobs-table">
          <thead><tr><th>ID</th><th>Tipo</th><th>Estado</th><th>Progreso</th><th>Inicio</th><th>Fin</th><th>Mensaje / error</th></tr></thead>
          <tbody>
            {jobs.map(job => (
              <tr key={job.id}>
                <td>{job.id}</td>
                <td>{job.job_type}</td>
                <td>{job.status}</td>
                <td>{Math.round((job.progress || 0) * 100)}%</td>
                <td>{job.started_at ? job.started_at.replace('T',' ').slice(0,19) : '-'}</td>
                <td>{job.finished_at ? job.finished_at.replace('T',' ').slice(0,19) : '-'}</td>
                <td>{job.error || job.message || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  </div>
}