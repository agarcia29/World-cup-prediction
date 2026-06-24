import React from 'react'

export default function TopScorelinesTable({ rows, homeTeam, awayTeam }) {
  if (!rows?.length) return null
  return (
    <div className="card">
      <div className="section-head">
        <div>
          <h3>Marcadores más probables</h3>
          <p>Top 10 scorelines según la simulación Poisson del ensemble.</p>
        </div>
      </div>
      <table className="table">
        <thead>
          <tr><th>{homeTeam}</th><th>{awayTeam}</th><th>Probabilidad</th></tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <td>{r.home_goals}</td>
              <td>{r.away_goals}</td>
              <td>{(r.probability * 100).toFixed(2)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
