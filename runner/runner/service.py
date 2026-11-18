from __future__ import annotations

import os
import shutil
import subprocess
import threading
import uuid
from pathlib import Path

from .agent import build_prompt, parse_outcome
from .models import RunResult, RunStatus, StartTask


class FactoryRunner:
    def __init__(self) -> None:
        self.repo_url = os.environ.get("FACTORY_REPO_URL", "")
        self.runs_dir = Path(os.environ.get("FACTORY_RUNS_DIR", "../factory-runs")).resolve()
        self.timeout_seconds = int(os.environ.get("FACTORY_MAX_RUN_SECONDS", "1800"))
        self._lock = threading.Lock()
        self._active_run_id: str | None = None
        self._results: dict[str, RunResult] = {}

    def start(self, task: StartTask) -> RunResult:
        if not self.repo_url:
            raise RuntimeError("FACTORY_REPO_URL is not configured.")
        with self._lock:
            if self._active_run_id:
                raise RuntimeError("Another task is already building.")
            run_id = str(uuid.uuid4())
            result = RunResult(run_id=run_id, issue_number=task.issue_number, status=RunStatus.running, message="Runner accepted task.")
            self._results[run_id] = result
            self._active_run_id = run_id
        threading.Thread(target=self._run, args=(run_id, task), daemon=True).start()
        return result

    def get(self, run_id: str) -> RunResult | None:
        return self._results.get(run_id)

    def _run(self, run_id: str, task: StartTask) -> None:
        run_dir = self.runs_dir / run_id
        try:
            self.runs_dir.mkdir(parents=True, exist_ok=True)
            self._command(["git", "clone", "--quiet", self.repo_url, str(run_dir)])
            self._command(["git", "checkout", "-b", f"issue-{task.issue_number}"], cwd=run_dir)
            prompt_path = run_dir / ".factory-prompt.txt"
            prompt_path.write_text(build_prompt(task.issue_number, task.title, task.specification, task.answer), encoding="utf-8")
            completed = subprocess.run(
                ["codex", "exec", "--output-last-message", str(run_dir / ".factory-output.txt"), "-"],
                cwd=run_dir,
                input=prompt_path.read_text(encoding="utf-8"),
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
            output = completed.stdout + "\n" + completed.stderr
            output_file = run_dir / ".factory-output.txt"
            if output_file.exists():
                output += "\n" + output_file.read_text(encoding="utf-8", errors="replace")
            if completed.returncode != 0:
                self._finish(run_id, task.issue_number, "stuck", f"Codex exited with code {completed.returncode}.")
                return
            outcome = parse_outcome(output)
            if outcome.status == "done":
                self._command(["git", "push", "-u", "origin", f"issue-{task.issue_number}"], cwd=run_dir)
                pr_url = self._open_pr(run_dir, task)
                self._finish(run_id, task.issue_number, "done", outcome.message, pr_url)
            else:
                self._finish(run_id, task.issue_number, outcome.status, outcome.message)
        except subprocess.TimeoutExpired:
            self._finish(run_id, task.issue_number, "stuck", f"Run exceeded {self.timeout_seconds // 60} minutes.")
        except Exception as exc:  # surfaced to n8n; detailed stdout remains in the run directory
            self._finish(run_id, task.issue_number, "stuck", f"Runner error: {exc}")
        finally:
            # Keep failed workspaces for diagnosis. Successful work is already pushed and can be removed.
            current = self._results[run_id]
            if current.status == RunStatus.done:
                shutil.rmtree(run_dir, ignore_errors=True)
            with self._lock:
                self._active_run_id = None

    @staticmethod
    def _command(command: list[str], cwd: Path | None = None) -> None:
        subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)

    @staticmethod
    def _open_pr(run_dir: Path, task: StartTask) -> str:
        command = ["gh", "pr", "create", "--base", "main", "--head", f"issue-{task.issue_number}", "--title", f"#{task.issue_number}: {task.title}", "--body", f"Closes #{task.issue_number}\n\nAutomated factory run. Review tests and diff before merging."]
        completed = subprocess.run(command, cwd=run_dir, check=True, text=True, capture_output=True)
        return completed.stdout.strip()

    def _finish(self, run_id: str, issue_number: int, status: str, message: str, pr_url: str | None = None) -> None:
        self._results[run_id] = RunResult(run_id=run_id, issue_number=issue_number, status=RunStatus(status), message=message, pull_request_url=pr_url)
