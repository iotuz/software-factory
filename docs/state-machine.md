# Issue state machine

The issue label is the source of truth. Each issue has exactly one factory-state label.

| State | Set by | Meaning / allowed next state |
|---|---|---|
| `Ideas` | Human | Rough task. n8n moves it to `Refining`. |
| `Refining` | n8n | AI produces a structured draft and questions, then n8n moves it to `Ready for approval`. Human discussion returns it here. |
| `Ready for approval` | n8n | Human checks the rewritten task. Only the human may label it `Approved`. |
| `Approved` | Human | Queued work. The start flow selects only one issue without another active build. |
| `Building` | n8n | Runner owns an active run on branch `issue-N`. |
| `Waiting for you` | n8n | Agent needs a written answer. A new human comment returns it to `Approved`. |
| `Stuck` | n8n | Timeout, command failure, or invalid agent result. Human retries via `Approved` or closes the issue. |
| `Your QA` | n8n | Pull request exists. Human merges, closes, or comments and returns issue to `Approved`. |
| `Done` | n8n | PR merged or issue closed. |

## Invariants

- The factory never applies `Approved`; that is a human decision.
- At most one open issue may be `Building`.
- A runner may push only an `issue-N` branch and open a PR; it never merges.
- Every automated label change and runner result is recorded as an issue comment.
