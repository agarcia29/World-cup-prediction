from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import traceback
from typing import Callable, Any
from src.utils.constants import MODELS_DIR
from src.utils.io import save_json

JOBS_PATH = MODELS_DIR / 'jobs.json'

@dataclass
class JobRecord:
    id: int
    job_type: str
    status: str
    started_at: str
    finished_at: str | None = None
    meta: dict | None = None
    error: str | None = None

class JobService:
    def __init__(self):
        self.jobs_path = JOBS_PATH
        self.jobs_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self):
        if not self.jobs_path.exists():
            return []
        import json
        return json.loads(self.jobs_path.read_text(encoding='utf-8'))

    def _save(self, jobs):
        save_json(self.jobs_path, jobs)

    def list_jobs(self):
        return list(reversed(self._load()))

    def run_job(self, job_type: str, func: Callable[[], Any], meta: dict | None = None):
        jobs = self._load()
        job_id = (max([j['id'] for j in jobs], default=0) + 1)
        rec = JobRecord(id=job_id, job_type=job_type, status='running', started_at=datetime.utcnow().isoformat(), meta=meta or {})
        jobs.append(asdict(rec))
        self._save(jobs)
        try:
            result = func()
            jobs[-1]['status'] = 'completed'
            jobs[-1]['finished_at'] = datetime.utcnow().isoformat()
            if isinstance(result, dict):
                jobs[-1]['meta'] = {**jobs[-1].get('meta', {}), **result}
            self._save(jobs)
            return jobs[-1]
        except Exception as exc:
            jobs[-1]['status'] = 'failed'
            jobs[-1]['finished_at'] = datetime.utcnow().isoformat()
            jobs[-1]['error'] = ''.join(traceback.format_exception_only(type(exc), exc)).strip()
            self._save(jobs)
            raise
