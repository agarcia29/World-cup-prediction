from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json, traceback, threading
from typing import Callable, Any
from src.utils.constants import DATA_DIR
from src.utils.io import save_json

JOBS_DIR = DATA_DIR / 'jobs'
JOBS_PATH = JOBS_DIR / 'jobs.json'

@dataclass
class JobRecord:
    id: int
    job_type: str
    status: str
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None
    progress: float = 0.0
    message: str = 'Queued'
    meta: dict | None = None
    error: str | None = None

class JobService:
    def __init__(self):
        self.jobs_path = JOBS_PATH
        self.jobs_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _load(self):
        if not self.jobs_path.exists():
            return []
        return json.loads(self.jobs_path.read_text(encoding='utf-8'))

    def _save(self, jobs):
        save_json(self.jobs_path, jobs)

    def list_jobs(self):
        return list(reversed(self._load()))

    def get_job(self, job_id: int):
        for job in self._load():
            if job['id'] == job_id:
                return job
        return None

    def _update(self, job_id: int, **updates):
        with self._lock:
            jobs = self._load()
            for idx, job in enumerate(jobs):
                if job['id'] == job_id:
                    jobs[idx] = {**job, **updates}
                    self._save(jobs)
                    return jobs[idx]
        return None

    def create_job(self, job_type: str, meta: dict | None = None):
        with self._lock:
            jobs = self._load()
            job_id = max([j['id'] for j in jobs], default=0) + 1
            rec = JobRecord(id=job_id, job_type=job_type, status='queued', created_at=datetime.utcnow().isoformat(), meta=meta or {})
            jobs.append(asdict(rec))
            self._save(jobs)
        return rec

    def _runner(self, job_id: int, func: Callable[[], Any]):
        self._update(job_id, status='running', started_at=datetime.utcnow().isoformat(), progress=0.1, message='Running')
        try:
            result = func()
            merged_meta = self.get_job(job_id).get('meta', {}) or {}
            if isinstance(result, dict):
                merged_meta = {**merged_meta, **result}
            self._update(job_id, status='completed', finished_at=datetime.utcnow().isoformat(), progress=1.0, message='Completed', meta=merged_meta)
        except Exception as exc:
            self._update(job_id, status='failed', finished_at=datetime.utcnow().isoformat(), progress=1.0, message='Failed', error=''.join(traceback.format_exception_only(type(exc), exc)).strip())

    def enqueue(self, job_type: str, func: Callable[[], Any], meta: dict | None = None):
        rec = self.create_job(job_type, meta)
        thread = threading.Thread(target=self._runner, args=(rec.id, func), daemon=True)
        thread.start()
        return self.get_job(rec.id)

    def run_sync(self, job_type: str, func: Callable[[], Any], meta: dict | None = None):
        rec = self.create_job(job_type, meta)
        self._runner(rec.id, func)
        return self.get_job(rec.id)