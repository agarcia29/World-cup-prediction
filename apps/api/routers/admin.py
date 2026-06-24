from fastapi import APIRouter, UploadFile, File, HTTPException
from apps.api.services.admin_service import AdminService
from apps.api.services.job_service import JobService
from apps.api.schemas.admin import AddMatchRequest

router = APIRouter(prefix='/admin', tags=['admin'])
admin = AdminService()
jobs = JobService()

@router.get('/dataset-summary')
def dataset_summary():
    return admin.dataset_summary()

@router.get('/jobs')
def list_jobs():
    return {'jobs': jobs.list_jobs()}

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
        return jobs.run_job('rebuild_features', admin.rebuild_features)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/retrain-xgb')
def retrain_xgb():
    try:
        return jobs.run_job('retrain_xgb', admin.retrain_xgb)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/retrain-bayes')
def retrain_bayes():
    try:
        return jobs.run_job('retrain_bayes_baseline', admin.retrain_bayes_baseline)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post('/refresh-teams')
def refresh_teams():
    try:
        return jobs.run_job('refresh_teams', admin.refresh_teams)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
