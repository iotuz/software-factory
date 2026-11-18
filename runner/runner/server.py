from fastapi import FastAPI, HTTPException

from .models import RunResult, StartTask
from .service import FactoryRunner

app = FastAPI(title="Software Factory Runner", version="0.1.0")
runner = FactoryRunner()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/runs", response_model=RunResult, status_code=202)
def start_run(task: StartTask) -> RunResult:
    try:
        return runner.start(task)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/runs/{run_id}", response_model=RunResult)
def get_run(run_id: str) -> RunResult:
    result = runner.get(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Unknown run ID.")
    return result
