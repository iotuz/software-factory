# n8n workflow imports

Target: n8n 1.x. All exports are inactive and contain no credential bindings or secrets.

Before activating any workflow, set the following environment variables in the n8n container and restart it:

- `FACTORY_REPOSITORY` — `owner/repository`
- `FACTORY_RUNNER_URL` — `http://host.docker.internal:8080`
- `GITHUB_TOKEN` — a fine-grained token with Issues and Pull Requests read/write permission for this repository
- `OPENAI_API_KEY` and `OPENAI_MODEL` — for the refinement workflow

The HTTP Request nodes deliberately use environment expressions so importing the public JSON cannot expose a token. For an exam demonstration, open each HTTP Request node after import and confirm its request options against your installed n8n version.

| File | Schedule | Purpose |
|---|---|---|
| `basic-a-refine.json` | every 5 minutes | Finds `Ideas`; creates an AI prompt payload. Add an OpenAI Chat Model node in the marked slot, then post its Markdown as an issue comment and set `Ready for approval`. |
| `basic-b-start.json` | every 2 minutes | Starts the oldest `Approved` issue only when no issue is `Building`. |
| `basic-b-collect.json` | every 2 minutes | Polls the runner and maps `done`, `question`, and `stuck` to issue comments/labels. |
| `track-pull-requests.json` | every 5 minutes | Finds PRs for `issue-N` branches and moves their issues to `Your QA` or `Done`. |
| `runner-event-fixture.json` | manual only | Safe fixture for validating valid, duplicate, and malformed runner events. |

The provided JSON files are deliberately safe, importable workflow **skeletons**: they model the schedule, input/output contracts and state guards. The post-import GitHub/AI response mapping is a small UI configuration step because node parameter schemas vary across n8n 1.x releases. Keep the finished, manually exported workflows committed here after you bind credentials and test them.

Run `runner-event-fixture.json` in a disposable n8n instance before connecting a real runner. Its expected outputs are, in order: `run-001` accepted; the second `run-001` duplicate; and the malformed final record rejected. The duplicate guard applies only within that one execution. For cross-execution idempotency, store handled run IDs durably (for example in a n8n Data Table) before writing a GitHub comment or changing a label.
