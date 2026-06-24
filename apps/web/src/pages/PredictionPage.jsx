import React, { useEffect, useMemo, useState } from 'react'
import { fetchTeams, fetchFixtures, fetchModelInfo, predictMatch } from '../api/client'
import ProbabilityCards from '../components/ProbabilityCards'
import TopScorelinesTable from '../components/TopScorelinesTable'
import ScoreHeatmap from '../components/ScoreHeatmap'
import GoalDistributionChart from '../components/GoalDistributionChart'
import InsightsPanel from '../components/InsightsPanel'
import FixtureStrip from '../components/FixtureStrip'

const TOURNAMENTS = [
  'FIFA World Cup',
  'FIFA World Cup qualification',
  'UEFA Euro',
  'Copa América',
  'UEFA Nations League',
  'Friendly'
]

const INITIAL_FORM = {
  home_team: 'Brazil',
  away_team: 'France',
  neutral: true,
  tournament: 'FIFA World Cup',
  month: 6,
}

export default function PredictionPage() {
  const [teams, setTeams] = useState([])
  const [fixtures, setFixtures] = useState([])
  const [modelInfo, setModelInfo] = useState(null)
  const [form, setForm] = useState(INITIAL_FORM)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([fetchTeams(), fetchFixtures(), fetchModelInfo()])
      .then(([teamsData, fixturesData, info]) => {
        setTeams(teamsData)
        setFixtures(fixturesData)
        setModelInfo(info)
      })
      .catch(err => setError(err.message))
  }, [])

  useEffect(() => {
    if (teams.length && !teams.includes(form.home_team)) {
      setForm(f => ({ ...f, home_team: teams[0], away_team: teams[1] || teams[0] }))
    }
  }, [teams])

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await predictMatch(form)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const heroCopy = useMemo(() => {
    if (!result) return 'Selecciona un partido para estimar goles esperados, scorelines y probabilidades 1X2.'
    return `${result.input.home_team} vs ${result.input.away_team} · xG ${result.expected_goals.home.toFixed(2)} - ${result.expected_goals.away.toFixed(2)}`
  }, [result])

  return (
    <div className="page">
      <header className="hero hero-grid">
        <div>
          <p className="eyebrow">Entrega 6</p>
          <h1>World Cup Predictor</h1>
          <p className="subtitle">{heroCopy}</p>
        </div>
        <div className="hero-side card compact">
          <div className="mini-stat"><span>Ventana de datos</span><strong>{modelInfo?.data_window || '2018+'}</strong></div>
          <div className="mini-stat"><span>Modelo Bayes</span><strong>{modelInfo?.models?.bayes?.includes('PyMC') ? 'Baseline + PyMC' : 'Baseline'}</strong></div>
          <div className="mini-stat"><span>XGBoost</span><strong>Home / Away regressors</strong></div>
        </div>
      </header>

      <FixtureStrip fixtures={fixtures} onPick={(fx) => setForm({
        home_team: fx.home_team,
        away_team: fx.away_team,
        neutral: fx.neutral ?? true,
        tournament: fx.tournament || 'FIFA World Cup',
        month: fx.month || 6,
      })} />

      <section className="card">
        <div className="section-head">
          <div>
            <h3>Predecir partido</h3>
            <p>Puedes editar los partidos sugeridos o armar uno manualmente.</p>
          </div>
        </div>
        <form className="form-grid" onSubmit={onSubmit}>
          <label>
            Equipo local
            <select value={form.home_team} onChange={e => setForm({...form, home_team: e.target.value})}>
              {teams.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </label>
          <label>
            Equipo visitante
            <select value={form.away_team} onChange={e => setForm({...form, away_team: e.target.value})}>
              {teams.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </label>
          <label>
            Torneo
            <select value={form.tournament} onChange={e => setForm({...form, tournament: e.target.value})}>
              {TOURNAMENTS.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </label>
          <label>
            Mes
            <input type="number" min="1" max="12" value={form.month} onChange={e => setForm({...form, month: Number(e.target.value)})}/>
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={form.neutral} onChange={e => setForm({...form, neutral: e.target.checked})}/>
            Sede neutral
          </label>
          <button className="primary" disabled={loading || form.home_team === form.away_team}>{loading ? 'Calculando…' : 'Predecir partido'}</button>
        </form>
        {form.home_team === form.away_team && <p className="error">Elige dos equipos distintos.</p>}
        {error && <p className="error">{error}</p>}
      </section>

      {result && (
        <>
          <ProbabilityCards probabilities={result.probabilities_1x2} xg={result.expected_goals} markets={result.market_probs} />
          <div className="grid two">
            <ScoreHeatmap matrix={result.score_matrix} homeTeam={result.input.home_team} awayTeam={result.input.away_team} />
            <TopScorelinesTable rows={result.top_scorelines} homeTeam={result.input.home_team} awayTeam={result.input.away_team} />
          </div>
          <div className="grid two">
            <GoalDistributionChart distributions={result.goal_distributions} homeTeam={result.input.home_team} awayTeam={result.input.away_team} />
            <InsightsPanel insights={result.insights} breakdown={result.model_breakdown} />
          </div>
        </>
      )}
    </div>
  )
}
