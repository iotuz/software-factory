from __future__ import annotations

import json
import re
from dataclasses import dataclass

RESULT_PREFIX = "FACTORY_RESULT:"


@dataclass(frozen=True)
class AgentOutcome:
    status: str
    message: str


def build_prompt(issue_number: int, title: str, specification: str, answer: str | None) -> str:
    answer_section = f"\nHuman answer to an earlier question:\n{answer}\n" if answer else ""
    return f"""You are the coding agent for GitHub issue #{issue_number}: {title}.

Implement only the approved specification below in the current repository and branch. Inspect existing code first. Write or update relevant tests and run the most appropriate checks. Do not merge, change GitHub labels, change credentials, or work outside this repository.

If a material ambiguity prevents safe implementation, stop and ask one concise question rather than guessing.

Approved specification:
{specification}
{answer_section}
At the very end, print exactly one machine-readable line:
FACTORY_RESULT: {{"status":"done"|"question"|"stuck", "message":"short human-readable summary"}}
Use status `done` only when changes are ready for review. Before `done`, commit the changes with a descriptive commit message. Use `question` when human input is required. Use `stuck` when you cannot safely continue.
"""


def parse_outcome(output: str) -> AgentOutcome:
    matches = re.findall(rf"^{re.escape(RESULT_PREFIX)}\s*(\{{.*\}})\s*$", output, re.MULTILINE)
    if not matches:
        return AgentOutcome("stuck", "Agent ended without a FACTORY_RESULT marker.")
    try:
        result = json.loads(matches[-1])
    except json.JSONDecodeError:
        return AgentOutcome("stuck", "Agent produced invalid FACTORY_RESULT JSON.")
    status = result.get("status")
    message = result.get("message")
    if status not in {"done", "question", "stuck"} or not isinstance(message, str) or not message.strip():
        return AgentOutcome("stuck", "Agent produced an incomplete FACTORY_RESULT.")
    return AgentOutcome(status, message.strip())
