from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from apps.api.services.admin_service import AdminService
from apps.api.services.job_service import JobService
from apps.api.schemas.admin import AddMatchRequest
from apps.api.core.config import get_settings

router = APIRouter(prefix='/admin', tags=['admin'])
admin = AdminService()
jobs = JobService()
settings = get_settings()

def _run_job(name: str, func):
    if settings.enable_async_jobs:
        return jobs.enqueue(name, func)
    return jobs.run_sync(name, func)

@router.get('/dataset-summary')
def dataset_summary():
    return admin.dataset_summary()

@router.get('/models-summary')
def models_summary():
    return {'models': admin.models_summary()}

@router.get('/jobs')
def list_jobs():
    return {'jobs': jobs.list_jobs()}

@router.get('/jobs/{job_id}')
def get_job(job_id: int):
    job = jobs.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Job no encontrado')
    return job

@router.post('/upload-results')
async def upload_results(results: UploadFile | None = File(default=None), goalscorers: UploadFile | None = File(default=None), shootouts: UploadFile | None = File(default=None)):
    uploaded = []
    try:
        if results:
            uploaded.append(await admin.upload_csv(results, 'results.csv'))
        if goalscorers:
            uploaded.append(await admin.upload_csv(goalscorers, 'goalscorers.csv'))
        if shootouts:
            uploaded.append(await admin.upload_csv(shootouts, 'shootouts.csv'))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {'uploaded': uploaded}

@router.post('/upload-model')
async def upload_model(slot: str = Form(...), model_file: UploadFile = File(...)):
    try:
        result = await admin.upload_model(slot, model_file)
        return {'ok': True, **result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post('/add-match')
def add_match(payload: AddMatchRequest):
    try:
        result = admin.add_match(payload.model_dump())
        return {'ok': True, **result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post('/rebuild-features')
def rebuild_features():
    try:
        return _run_job('rebuild_features', admin.rebuild_features)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/retrain-xgb')
def retrain_xgb():
    try:
        return _run_job('retrain_xgb', admin.retrain_xgb)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/retrain-bayes')
def retrain_bayes():
    try:
        return _run_job('retrain_bayes_baseline', admin.retrain_bayes_baseline)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/retrain-bayes-heavy')
def retrain_bayes_heavy():
    if settings.is_production or settings.disable_heavy_bayes:
        raise HTTPException(status_code=403, detail='Bayes pesado desactivado en producción. Entrénalo localmente y súbelo desde Admin > Modelos.')
    raise HTTPException(status_code=501, detail='Entrenamiento Bayes pesado no expuesto por API en esta entrega.')

@router.post('/refresh-teams')
def refresh_teams():
    try:
        return _run_job('refresh_teams', admin.refresh_teams)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))