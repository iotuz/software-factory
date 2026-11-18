# Architecture

```mermaid
flowchart LR
  GH[GitHub: issues, labels, comments, PRs] <-->|scheduled reads / writes| N[n8n: orchestration and AI refinement]
  N <-->|start task / poll result| R[Runner: HTTP service]
  R -->|prompt, isolated issue-N worktree| C[Codex CLI]
  C -->|commit, push, PR via gh| GH
```

n8n remains the state authority. The runner has a narrow responsibility: create a disposable worktree, run one coding-agent invocation for at most 30 minutes, and return a structured result. GitHub is the auditable system of record.
