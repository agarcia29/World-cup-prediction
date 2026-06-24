import React from 'react'

export default function InsightsPanel({ insights, breakdown }) {
  if (!insights) return null
  const items = [
    ['Diferencia Elo', insights.elo_diff],
    ['GF recientes local (5)', insights.home_recent_gf_5],
    ['GF recientes visitante (5)', insights.away_recent_gf_5],
    ['GA recientes local (5)', insights.home_recent_ga_5],
    ['GA recientes visitante (5)', insights.away_recent_ga_5],
    ['Dif. puntos forma (5)', insights.points_form_diff_5],
    ['Bayes activo', insights.bayes_source],
  ]
  return (
    <div className="card">
      <div className="section-head">
        <div>
          <h3>Señales del modelo</h3>
          <p>Indicadores rápidos para entender de dónde sale la predicción.</p>
        </div>
      </div>
      <div className="insight-grid">
        {items.map(([label, value]) => (
          <div className="insight-item" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
      {breakdown && (
        <div className="breakdown-grid">
          <div className="break-card">
            <span>Bayes</span>
            <strong>{breakdown.bayes_home_xg} / {breakdown.bayes_away_xg}</strong>
          </div>
          <div className="break-card">
            <span>XGBoost</span>
            <strong>{breakdown.xgb_home_xg} / {breakdown.xgb_away_xg}</strong>
          </div>
        </div>
      )}
    </div>
  )
}
