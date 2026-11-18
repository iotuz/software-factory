from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    running = "running"
    done = "done"
    question = "question"
    stuck = "stuck"


class StartTask(BaseModel):
    issue_number: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=300)
    specification: str = Field(min_length=1)
    answer: str | None = None


class RunResult(BaseModel):
    run_id: str
    issue_number: int
    status: RunStatus
    message: str
    pull_request_url: str | None = None
