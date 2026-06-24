import React, { useEffect, useState } from 'react'
import { compareMatches, fetchFixtures, fetchTeams } from '../api/client'

const EMPTY = { home_team:'Brazil', away_team:'France', neutral:true, tournament:'FIFA World Cup', month:6 }

export default function MultiPredictionPage() {
  const [teams, setTeams] = useState([])
  const [fixtures, setFixtures] = useState([])
  const [rows, setRows] = useState([EMPTY])
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => { Promise.all([fetchTeams(), fetchFixtures()]).then(([t, f]) => {setTeams(t); setFixtures(f)}).catch(e => setError(e.message)) }, [])

  function updateRow(idx, patch) { setRows(prev => prev.map((r,i)=> i===idx ? {...r, ...patch} : r)) }
  function addRow(prefill=EMPTY) { setRows(prev => [...prev, {...prefill}]) }
  function removeRow(idx) { setRows(prev => prev.filter((_,i)=>i!==idx)) }

  async function runCompare() {
    setLoading(true); setError('')
    try {
      const data = await compareMatches(rows)
      const enriched = (data.matches || []).map((m) => ({
        home_team: m.input.home_team,
        away_team: m.input.away_team,
        xg_home: m.expected_goals.home,
        xg_away: m.expected_goals.away,
        home_win: m.probabilities_1x2.home_win,
        draw: m.probabilities_1x2.draw,
        away_win: m.probabilities_1x2.away_win,
        over_2_5: m.market_probs.over_2_5,
        btts_yes: m.market_probs.btts_yes,
        top_scoreline: `${m.top_scorelines[0]?.home_goals ?? 0}-${m.top_scorelines[0]?.away_goals ?? 0}`,
        confidence: Math.max(m.probabilities_1x2.home_win, m.probabilities_1x2.draw, m.probabilities_1x2.away_win),
      })).sort((a,b)=>b.confidence-a.confidence)
      setResults(enriched)
    } catch (e) { setError(e.message) } finally { setLoading(false) }
  }

  function exportCsv() {
    const headers = ['home_team','away_team','xg_home','xg_away','home_win','draw','away_win','over_2_5','btts_yes','top_scoreline','confidence']
    const lines = [headers.join(',')].concat(results.map(r => headers.map(h => r[h]).join(',')))
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href=url; a.download='multi_prediction.csv'; a.click(); URL.revokeObjectURL(url)
  }

  return <div className="stack">
    <section className="card">
      <div className="section-head"><div><h3>Multi-predicción</h3><p>Arma una lista de partidos, compáralos y exporta el resumen a CSV.</p></div>
      <div className="actions-inline">
        <button className="secondary" onClick={() => addRow()}>+ Agregar partido</button>
        <button className="primary" onClick={runCompare} disabled={loading}>{loading ? 'Calculando…' : 'Comparar partidos'}</button>
      </div></div>
      {!!fixtures.length && <div className="fixture-grid" style={{marginBottom:14}}>{fixtures.map((fx, idx) => <button className="fixture-card" key={idx} onClick={() => addRow(fx)}><strong>{fx.home_team} vs {fx.away_team}</strong><small>{fx.tournament}</small></button>)}</div>}
      <div className="multi-list">{rows.map((row, idx) => <div className="multi-row" key={idx}>
        <select value={row.home_team} onChange={e=>updateRow(idx,{home_team:e.target.value})}>{teams.map(t=><option key={t}>{t}</option>)}</select>
        <select value={row.away_team} onChange={e=>updateRow(idx,{away_team:e.target.value})}>{teams.map(t=><option key={t}>{t}</option>)}</select>
        <input value={row.tournament} onChange={e=>updateRow(idx,{tournament:e.target.value})} />
        <input type="number" min="1" max="12" value={row.month} onChange={e=>updateRow(idx,{month:Number(e.target.value)})} />
        <label className="checkbox small"><input type="checkbox" checked={row.neutral} onChange={e=>updateRow(idx,{neutral:e.target.checked})}/>Neutral</label>
        <button className="ghost" onClick={() => removeRow(idx)}>Eliminar</button>
      </div>)}</div>
      {error && <p className="error">{error}</p>}
    </section>

    {results.length > 0 && <section className="card">
      <div className="section-head"><div><h3>Resumen comparativo</h3><p>Ordenado por la probabilidad más alta del mercado 1X2.</p></div><button className="secondary" onClick={exportCsv}>Exportar CSV</button></div>
      <table className="table"><thead><tr><th>Partido</th><th>xG</th><th>1X2</th><th>Over 2.5</th><th>BTTS</th><th>Scoreline</th><th>Confianza</th></tr></thead><tbody>
        {results.map((r, idx) => <tr key={idx}><td>{r.home_team} vs {r.away_team}</td><td>{r.xg_home.toFixed(2)} - {r.xg_away.toFixed(2)}</td><td>{(r.home_win*100).toFixed(1)} / {(r.draw*100).toFixed(1)} / {(r.away_win*100).toFixed(1)}</td><td>{(r.over_2_5*100).toFixed(1)}%</td><td>{(r.btts_yes*100).toFixed(1)}%</td><td>{r.top_scoreline}</td><td>{(r.confidence*100).toFixed(1)}%</td></tr>)}
      </tbody></table>
    </section>}
  </div>
}
