import React from 'react'
import Plot from 'react-plotly.js'

export default function ScoreHeatmap({ matrix, homeTeam, awayTeam }) {
  if (!matrix?.length) return null
  const labels = Array.from({ length: matrix.length }, (_, i) => i)
  return (
    <div className="card plot-card">
      <div className="section-head">
        <div>
          <h3>Matriz de marcadores</h3>
          <p>Probabilidad conjunta de cada scoreline.</p>
        </div>
      </div>
      <Plot
        data={[{
          z: matrix,
          x: labels,
          y: labels,
          type: 'heatmap',
          colorscale: 'Blues',
          hovertemplate: `${homeTeam} %{y} - %{x} ${awayTeam}<br>%{z:.2%}<extra></extra>`,
        }]}
        layout={{
          autosize: true,
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)',
          margin: { l: 50, r: 20, t: 10, b: 40 },
          font: { color: '#eef2ff' },
          xaxis: { title: awayTeam },
          yaxis: { title: homeTeam },
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '380px' }}
      />
    </div>
  )
}
