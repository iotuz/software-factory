# Software Factory

An exam-ready prototype of a human-controlled software factory. GitHub Issues hold tasks and their state; n8n orchestrates the flow; the runner starts Codex in an isolated worktree; GitHub pull requests are the review gate.

## What is included

- `workflows/` — inactive n8n workflow exports for the four required flows.
- `runner/` — a small HTTP service that starts one Codex run at a time and reports `done`, `question`, or `stuck`.
- `docs/` — architecture, issue-state rules, specification template, AI refinement prompt, and safety decisions for the report.
- `app/` — the deliberately small product area that factory tasks will change.

## First setup

1. Create a public GitHub repository from this directory and push `main`.
2. Create the labels in [`docs/state-machine.md`](docs/state-machine.md) exactly (including capitalization).
3. Copy `.env.example` to `.env`; fill in only local values. Never commit `.env`.
4. Run `docker compose up -d n8n`, open `http://localhost:5678`, and create GitHub/OpenAI credentials in n8n.
5. Import the JSON files in `workflows/`. They are intentionally inactive. Bind credentials in n8n and set `FACTORY_REPOSITORY` / `FACTORY_RUNNER_URL` environment variables before activating schedules.
6. Create a GitHub issue labelled `Ideas`, let the refinement flow produce a draft, then manually move it to `Approved` when satisfied.

## Local runner

The runner is only needed for Basic B. It must run where `git`, `gh`, and `codex` are installed and authenticated.

```bash
cd runner
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn runner.server:app --host 0.0.0.0 --port 8080
```

n8n in Docker reaches it at `http://host.docker.internal:8080` (not `localhost`). On Linux, the provided Compose file maps that name to the Docker host.

## Verification

```bash
PYTHONPATH=runner python3 -m unittest discover -s runner/tests -v
python3 /home/iotus/.codex/plugins/cache/openai-curated-remote/samautomation-workflows/1.0.0/skills/n8n-workflow-check/scripts/check_workflow.py workflows/basic-a-refine.json
```

The workflow checker is structural only: workflow imports and live GitHub/n8n execution still need to be performed with your own credentials.
