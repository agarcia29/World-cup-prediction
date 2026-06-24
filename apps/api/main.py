from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from apps.api.routers.health import router as health_router
from apps.api.routers.teams import router as teams_router
from apps.api.routers.predict import router as predict_router
from apps.api.routers.model_info import router as model_info_router
from apps.api.routers.fixtures import router as fixtures_router
from apps.api.routers.admin import router as admin_router

app = FastAPI(title='World Cup Predictor API', version='0.6.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(health_router)
app.include_router(teams_router)
app.include_router(predict_router)
app.include_router(model_info_router)
app.include_router(fixtures_router)
app.include_router(admin_router)

WEB_DIST = Path(__file__).resolve().parents[1] / 'web' / 'dist'
if WEB_DIST.exists():
    app.mount('/assets', StaticFiles(directory=WEB_DIST / 'assets'), name='assets')

    @app.get('/')
    def serve_frontend():
        return FileResponse(WEB_DIST / 'index.html')

    @app.get('/{full_path:path}')
    def spa_fallback(full_path: str):
        if full_path.startswith('api'):
            return {'detail': 'Not Found'}
        target = WEB_DIST / full_path
        if target.exists() and target.is_file():
            return FileResponse(target)
        return FileResponse(WEB_DIST / 'index.html')
