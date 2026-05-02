"""
Refactor Agent - Phase 2
Generates concrete refactoring proposals and draft PRs based on scan results.
"""

import json
from dataclasses import dataclass
from typing import Optional

from ..core.base_agent import BaseAgent
from ..core.models import ScanResult, RefactorProposal, Issue, Severity


SYSTEM_PROMPT = """You are a senior software engineer specializing in code refactoring.
Given a list of code issues, you will:
1. Prioritize issues by impact and effort
2. Generate specific, actionable refactoring suggestions with before/after code examples
3. Group related changes into coherent PR proposals
4. Estimate the effort (S/M/L/XL) for each change

Output structured JSON only. No prose outside the JSON block."""


@dataclass
class RefactorConfig:
    max_proposals_per_run: int = 10
    auto_create_pr: bool = False
    target_branch: str = "refactor/auto-{timestamp}"
    effort_threshold: str = "M"  # Only propose changes <= this effort


class RefactorAgent(BaseAgent):
    """
    Transforms raw scan results into actionable refactoring proposals.

    Uses LLM (MiMo / Claude) to:
    - Understand the semantic context of each issue
    - Generate idiomatic replacement code
    - Bundle related fixes into atomic PRs
    - Write PR descriptions with rationale
    """

    AGENT_NAME = "refactor_agent"
    VERSION = "0.2.4"

    EFFORT_RANK = {"S": 1, "M": 2, "L": 3, "XL": 4}

    def __init__(self, config: RefactorConfig, llm_client=None):
        super().__init__(llm_client=llm_client)
        self.config = config
        self.proposals: list[RefactorProposal] = []

    def run(self, scan_results: list[ScanResult]) -> list[RefactorProposal]:
        """Generate refactoring proposals from scan results."""
        prioritized = self._prioritize_issues(scan_results)
        self.logger.info(f"[RefactorAgent] Processing {len(prioritized)} prioritized issues")

        batches = self._group_into_batches(prioritized)
        for batch in batches[: self.config.max_proposals_per_run]:
            proposal = self._generate_proposal(batch)
            if proposal and self._within_effort(proposal.effort):
                self.proposals.append(proposal)

        self.logger.info(f"[RefactorAgent] Generated {len(self.proposals)} proposals")
        return self.proposals

    def _prioritize_issues(self, results: list[ScanResult]) -> list[Issue]:
        """Sort issues: HIGH security first, then MEDIUM perf, then tech debt."""
        all_issues = [issue for r in results for issue in r.issues]
        severity_order = {Severity.HIGH: 0, Severity.MEDIUM: 1, Severity.LOW: 2}
        category_order = {"security": 0, "performance": 1, "tech_debt": 2}
        return sorted(
            all_issues,
            key=lambda i: (severity_order.get(i.severity, 9), category_order.get(i.category, 9)),
        )

    def _group_into_batches(self, issues: list[Issue]) -> list[list[Issue]]:
        """Group related issues (same file / same rule) into batches."""
        by_file: dict[str, list[Issue]] = {}
        for issue in issues:
            by_file.setdefault(issue.file, []).append(issue)

        batches = []
        for file_issues in by_file.values():
            # Split large files into chunks of 5
            for i in range(0, len(file_issues), 5):
                batches.append(file_issues[i : i + 5])
        return batches

    def _generate_proposal(self, issues: list[Issue]) -> Optional[RefactorProposal]:
        """Call LLM to generate a concrete refactoring proposal."""
        if not self.llm_client:
            return self._mock_proposal(issues)

        issues_json = json.dumps([i.to_dict() for i in issues], indent=2)
        prompt = f"""Here are code issues found in a project:

{issues_json}

Generate a refactoring proposal as JSON with this schema:
{{
  "title": "short PR title",
  "description": "why this change matters",
  "effort": "S|M|L|XL",
  "changes": [
    {{
      "file": "path/to/file.py",
      "line": 42,
      "original": "original code snippet",
      "replacement": "improved code snippet",
      "explanation": "what changed and why"
    }}
  ]
}}"""

        response = self.llm_client.chat(
            system=SYSTEM_PROMPT,
            user=prompt,
            temperature=0.2,
        )
        try:
            data = json.loads(response)
            return RefactorProposal(
                title=data["title"],
                description=data["description"],
                effort=data.get("effort", "M"),
                changes=data.get("changes", []),
                source_issues=issues,
            )
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"Failed to parse LLM response: {e}")
            return None

    def _mock_proposal(self, issues: list[Issue]) -> RefactorProposal:
        """Fallback for when LLM client is not configured (demo mode)."""
        file_name = issues[0].file if issues else "unknown"
        return RefactorProposal(
            title=f"fix: address {len(issues)} issues in {file_name.split('/')[-1]}",
            description=(
                f"Automated refactoring proposal for {len(issues)} detected issues. "
                "Addresses security vulnerabilities, performance bottlenecks, and tech debt."
            ),
            effort="M",
            changes=[
                {
                    "file": i.file,
                    "line": i.line,
                    "original": i.snippet,
                    "replacement": f"# TODO: apply fix for rule '{i.rule}'",
                    "explanation": i.message,
                }
                for i in issues
            ],
            source_issues=issues,
        )

    def _within_effort(self, effort: str) -> bool:
        threshold = self.config.effort_threshold
        return self.EFFORT_RANK.get(effort, 99) <= self.EFFORT_RANK.get(threshold, 2)

    def to_markdown(self) -> str:
        """Render all proposals as a Markdown report."""
        if not self.proposals:
            return "No refactoring proposals generated."

        lines = ["# Refactoring Proposals\n"]
        for idx, p in enumerate(self.proposals, 1):
            lines.append(f"## {idx}. {p.title} (effort: {p.effort})\n")
            lines.append(f"{p.description}\n")
            lines.append("### Changes\n")
            for change in p.changes:
                lines.append(f"**{change['file']}** (line {change['line']})\n")
                lines.append(f"```python\n# Before\n{change['original']}\n\n# After\n{change['replacement']}\n```\n")
                lines.append(f"> {change['explanation']}\n")
            lines.append("---\n")
        return "\n".join(lines)
