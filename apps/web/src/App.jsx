import React, { useState } from 'react'
import PredictionPage from './pages/PredictionPage'
import MultiPredictionPage from './pages/MultiPredictionPage'
import AdminPage from './pages/AdminPage'
import './styles.css'

export default function App() {
  const [tab, setTab] = useState('prediction')
  return (
    <div className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">Entrega 6 · Render-ready</p>
          <h1>World Cup Predictor</h1>
          <p className="subtitle">Predicción individual, multi-predicción y panel admin para actualizar dataset y modelos.</p>
        </div>
        <nav className="tabbar">
          <button className={tab==='prediction'?'tab active':'tab'} onClick={() => setTab('prediction')}>Predicción</button>
          <button className={tab==='multi'?'tab active':'tab'} onClick={() => setTab('multi')}>Multi-predicción</button>
          <button className={tab==='admin'?'tab active':'tab'} onClick={() => setTab('admin')}>Admin</button>
        </nav>
      </header>
      {tab === 'prediction' && <PredictionPage />}
      {tab === 'multi' && <MultiPredictionPage />}
      {tab === 'admin' && <AdminPage />}
    </div>
  )
}
