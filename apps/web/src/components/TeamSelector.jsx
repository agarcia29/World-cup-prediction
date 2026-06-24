import React from 'react'
export default function TeamSelector({ label, value, onChange, teams }) {
  return (
    <label style={{ display: 'grid', gap: 6 }}>
      <span>{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">Selecciona...</option>
        {teams.map((team) => <option key={team} value={team}>{team}</option>)}
      </select>
    </label>
  );
}
