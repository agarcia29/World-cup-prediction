import React from 'react'
import Plot from 'react-plotly.js'

export default function GoalDistributionChart({ distributions, homeTeam, awayTeam }) {
  if (!distributions?.home?.length) return null
  const x = distributions.home.map((_, idx) => idx)
  return (
    <div className="card plot-card">
      <div className="section-head">
        <div>
          <h3>Distribución de goles</h3>
          <p>Probabilidad marginal de 0, 1, 2... goles por equipo.</p>
        </div>
      </div>
      <Plot
        data={[
          { x, y: distributions.home, type: 'bar', name: homeTeam },
          { x, y: distributions.away, type: 'bar', name: awayTeam },
        ]}
        layout={{
          barmode: 'group',
          autosize: true,
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)',
          margin: { l: 50, r: 20, t: 10, b: 40 },
          font: { color: '#eef2ff' },
          xaxis: { title: 'Goles' },
          yaxis: { title: 'Probabilidad', tickformat: '.0%' },
          legend: { orientation: 'h', y: 1.12 }
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '360px' }}
      />
    </div>
  )
}
