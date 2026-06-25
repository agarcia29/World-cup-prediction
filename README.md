# World Cup Predictor — Entrega 3

Proyecto para predecir partidos internacionales con un stack web moderno:

- **Frontend:** React + Vite
- **Backend:** FastAPI
- **Modelado:** XGBoost + capa Bayes
- **Datos:** repositorio `international_results` filtrado desde 2018

## Qué cambia en Entrega 3
### 1) Pipeline más sólido
- `team_snapshots.csv` para inferencia con estado reciente por selección
- rolling features causales (solo usan información anterior al partido)
- Elo pre-partido separado del resto del pipeline

### 2) Capa Bayes mejorada
- se mantiene un **fallback Poisson baseline** para no romper el MVP
- se agrega **script PyMC jerárquico con MCMC** (`scripts/03_train_bayes.py --pymc`)
- si existe `data/models/bayes_pymc.nc`, la API lo usa automáticamente

### 3) Backtesting temporal
- `src/evaluation/backtesting.py`
- `scripts/05_evaluate.py`
- split temporal por fecha (train antes de 2025, test desde 2025)

### 4) Frontend más usable
- formulario único de predicción
- tarjetas de probabilidades
- heatmap de scorelines
- panel de señales del modelo

---

## Flujo recomendado

### A. Preparar datos
```bash
python scripts/01_filter_data.py
python scripts/02_build_features.py
```

### B. Entrenar modelos
```bash
# baseline + artefacto Bayes rápido
python scripts/03_train_bayes.py

# si quieres entrenar el jerárquico con MCMC
python scripts/03_train_bayes.py --pymc --draws 1000 --tune 1000

# xgboost home/away
python scripts/04_train_xgb.py

# lista de equipos y artefactos auxiliares
python scripts/06_serve_prep.py
```

### C. Evaluar
```bash
python scripts/05_evaluate.py
```

### D. Levantar API
```bash
uvicorn apps.api.main:app --reload
```

### E. Levantar frontend
```bash
cd apps/web
npm install
npm run dev
```

---

## Endpoints
- `GET /health`
- `GET /teams`
- `GET /model-info`
- `POST /predict`

### Payload de ejemplo
```json
{
  "home_team": "Brazil",
  "away_team": "France",
  "neutral": true,
  "tournament": "FIFA World Cup",
  "month": 6
}
```

---

## Siguiente fase sugerida
1. incorporar **ponderación temporal exponencial** en las features
2. agregar **Bivariate Poisson / Dixon-Coles**
3. calibrar probabilidades 1X2 con backtesting rolling
4. integrar calendario de partidos del día y página “multi-match”


## Entrega 4
- `requirements.txt` corregido para evitar conflictos con PyMC.
- `requirements-bayes.txt` separado para el modelo Bayes pesado.
- Endpoint `GET /fixtures/today` para cargar partidos sugeridos desde `data/models/fixtures_today.json`.
- Endpoint `POST /compare` para predecir varios partidos en una sola llamada.
- Nuevas salidas en `/predict`: `market_probs` y `goal_distributions`.
- Frontend con heatmap y distribución de goles en Plotly.


## Entrega 6 – Admin, multi-predicción y despliegue en Render

### Novedades
- Panel **Admin** en la web para subir CSV, agregar partidos manualmente y ejecutar mantenimiento.
- Vista **Multi-predicción** para comparar varios partidos y exportar un CSV.
- Endpoints admin: `/admin/dataset-summary`, `/admin/jobs`, `/admin/upload-results`, `/admin/add-match`, `/admin/rebuild-features`, `/admin/retrain-xgb`, `/admin/retrain-bayes`, `/admin/refresh-teams`.
- Despliegue **Render-ready** en un solo web service: el frontend se compila con Vite y FastAPI sirve los archivos estáticos.

### Render (un solo Web Service)
1. Sube este repo a GitHub.
2. En Render crea un **Web Service** apuntando al repo.
3. Usa el `render.yaml` incluido o configura manualmente:
   - **Build Command**: `pip install -r requirements.txt && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs && cd apps/web && npm install && npm run build`
   - **Start Command**: `uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`
4. El frontend quedará servido desde la misma URL del backend.

### Desarrollo local
Backend:
```bash
pip install -r requirements.txt
uvicorn apps.api.main:app --reload
```

Frontend:
```bash
cd apps/web
npm install
npm run dev
```


## Entrega 7

### Variables de entorno nuevas
- `APP_ENV=production`
- `DISABLE_HEAVY_BAYES=true`
- `ENABLE_ASYNC_JOBS=true`

### Novedades
- Admin > Model Upload para subir artefactos (`xgb_home.pkl`, `xgb_away.pkl`, `feature_columns.json`, `bayes_baseline.json`, `bayes_pymc.nc`, `team_index.json`).
- Jobs asíncronos para `rebuild-features`, `retrain-xgb` y `refresh-teams` con estado persistido en `data/jobs/jobs.json`.
- Endpoint pesado de Bayes bloqueado en producción; la estrategia recomendada es entrenar localmente y subir el artefacto desde la web.
