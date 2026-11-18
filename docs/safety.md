# Permission and safety choices

- A human alone grants `Approved`; AI refinement cannot authorize implementation.
- The runner accepts a single configured repository URL and rejects non-positive issue numbers.
- One in-process run is allowed at a time; restarts report prior work as `stuck` rather than guessing.
- Each run uses a new `issue-N` branch under a disposable working directory.
- The agent may edit, test, commit, push its branch, and open a pull request. It may not merge, delete branches, change credentials, or modify GitHub labels directly.
- Runs receive a 30-minute hard timeout. Non-zero exits, malformed status markers, and timeouts become `stuck` for human handling.
- Secrets belong in n8n credentials, GitHub CLI authentication, or environment variables—never in workflow JSON or commits.
