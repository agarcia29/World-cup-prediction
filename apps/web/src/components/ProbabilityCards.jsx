import React from 'react'

function MetricCard({ label, value, tone = '' }) {
  return (
    <div className={`card stat ${tone}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  )
}

export default function ProbabilityCards({ probabilities, xg, markets }) {
  if (!probabilities) return null
  return (
    <>
      <div className="grid cards cards-5">
        <MetricCard label="Victoria local" value={`${(probabilities.home_win * 100).toFixed(1)}%`} tone="tone-home" />
        <MetricCard label="Empate" value={`${(probabilities.draw * 100).toFixed(1)}%`} tone="tone-draw" />
        <MetricCard label="Victoria visitante" value={`${(probabilities.away_win * 100).toFixed(1)}%`} tone="tone-away" />
        <MetricCard label="xG local" value={xg.home.toFixed(2)} />
        <MetricCard label="xG visitante" value={xg.away.toFixed(2)} />
      </div>
      {markets && (
        <div className="grid cards cards-4">
          <MetricCard label="Over 2.5" value={`${(markets.over_2_5 * 100).toFixed(1)}%`} />
          <MetricCard label="Under 2.5" value={`${(markets.under_2_5 * 100).toFixed(1)}%`} />
          <MetricCard label="BTTS Sí" value={`${(markets.btts_yes * 100).toFixed(1)}%`} />
          <MetricCard label="BTTS No" value={`${(markets.btts_no * 100).toFixed(1)}%`} />
        </div>
      )}
    </>
  )
}
