import React from 'react'

export default function FixtureStrip({ fixtures, onPick }) {
  if (!fixtures?.length) return null
  return (
    <section className="fixture-strip">
      <div className="section-head section-head-tight">
        <div>
          <h3>Partidos sugeridos</h3>
          <p>Se cargan desde <code>data/models/fixtures_today.json</code>. Haz clic para rellenar el formulario.</p>
        </div>
      </div>
      <div className="fixture-grid">
        {fixtures.map((fx, idx) => (
          <button className="fixture-card" key={`${fx.home_team}-${fx.away_team}-${idx}`} onClick={() => onPick(fx)}>
            <span className="fixture-label">{fx.label || fx.tournament}</span>
            <strong>{fx.home_team} vs {fx.away_team}</strong>
            <small>{fx.tournament}</small>
          </button>
        ))}
      </div>
    </section>
  )
}
