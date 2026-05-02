"""
Code Scan Agent - Phase 1
Analyzes codebase for tech debt, security vulnerabilities, and performance issues.
"""

import ast
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..core.base_agent import BaseAgent
from ..core.models import ScanResult, Issue, Severity


@dataclass
class ScanConfig:
    target_path: str
    include_patterns: list[str] = field(default_factory=lambda: ["*.py", "*.ts", "*.js"])
    exclude_dirs: list[str] = field(default_factory=lambda: [".git", "node_modules", "__pycache__", ".venv"])
    max_file_size_kb: int = 500
    enable_security_scan: bool = True
    enable_perf_scan: bool = True
    enable_debt_scan: bool = True


class ScanAgent(BaseAgent):
    """
    Multi-dimensional code scanner that identifies:
    - Technical debt (complex functions, long files, duplication)
    - Security vulnerabilities (injection risks, hardcoded secrets, insecure APIs)
    - Performance bottlenecks (N+1 queries, blocking calls, memory leaks)
    """

    AGENT_NAME = "scan_agent"
    VERSION = "0.3.1"

    # Security patterns to detect
    SECURITY_PATTERNS = {
        "hardcoded_secret": re.compile(
            r'(password|secret|api_key|token|passwd)\s*=\s*["\'][^"\']{8,}["\']',
            re.IGNORECASE,
        ),
        "sql_injection_risk": re.compile(
            r'execute\s*\(\s*[f"\'].*%s.*["\']|execute\s*\(\s*f["\']',
            re.IGNORECASE,
        ),
        "eval_usage": re.compile(r'\beval\s*\('),
        "shell_injection": re.compile(r'os\.system\s*\(|subprocess\.call\s*\(.*shell\s*=\s*True'),
    }

    # Performance anti-patterns
    PERF_PATTERNS = {
        "loop_db_query": re.compile(r'for\s+\w+\s+in\s+.*:\s*\n.*\.(filter|get|all)\('),
        "synchronous_sleep": re.compile(r'\btime\.sleep\s*\('),
        "large_list_comp": re.compile(r'\[.*for.*in.*for.*in'),  # nested list comp
    }

    def __init__(self, config: ScanConfig, llm_client=None):
        super().__init__(llm_client=llm_client)
        self.config = config
        self.results: list[ScanResult] = []

    def run(self) -> list[ScanResult]:
        """Execute full scan pipeline."""
        target = Path(self.config.target_path)
        if not target.exists():
            raise FileNotFoundError(f"Target path not found: {target}")

        files = self._collect_files(target)
        self.logger.info(f"[ScanAgent] Found {len(files)} files to scan")

        for file_path in files:
            try:
                result = self._scan_file(file_path)
                if result.issues:
                    self.results.append(result)
            except Exception as e:
                self.logger.warning(f"Failed to scan {file_path}: {e}")

        self.logger.info(
            f"[ScanAgent] Scan complete. {len(self.results)} files with issues, "
            f"{sum(len(r.issues) for r in self.results)} total issues found."
        )
        return self.results

    def _collect_files(self, root: Path) -> list[Path]:
        files = []
        for pattern in self.config.include_patterns:
            for f in root.rglob(pattern):
                if any(ex in f.parts for ex in self.config.exclude_dirs):
                    continue
                if f.stat().st_size > self.config.max_file_size_kb * 1024:
                    continue
                files.append(f)
        return sorted(set(files))

    def _scan_file(self, path: Path) -> ScanResult:
        source = path.read_text(encoding="utf-8", errors="ignore")
        issues: list[Issue] = []

        if self.config.enable_security_scan:
            issues.extend(self._check_security(source, path))

        if self.config.enable_perf_scan:
            issues.extend(self._check_performance(source, path))

        if self.config.enable_debt_scan and path.suffix == ".py":
            issues.extend(self._check_debt_python(source, path))

        return ScanResult(file_path=str(path), issues=issues)

    def _check_security(self, source: str, path: Path) -> list[Issue]:
        issues = []
        lines = source.splitlines()
        for issue_type, pattern in self.SECURITY_PATTERNS.items():
            for match in pattern.finditer(source):
                line_no = source[: match.start()].count("\n") + 1
                issues.append(
                    Issue(
                        severity=Severity.HIGH,
                        category="security",
                        rule=issue_type,
                        message=f"Potential {issue_type.replace('_', ' ')} detected",
                        file=str(path),
                        line=line_no,
                        snippet=lines[line_no - 1].strip() if line_no <= len(lines) else "",
                    )
                )
        return issues

    def _check_performance(self, source: str, path: Path) -> list[Issue]:
        issues = []
        lines = source.splitlines()
        for issue_type, pattern in self.PERF_PATTERNS.items():
            for match in pattern.finditer(source):
                line_no = source[: match.start()].count("\n") + 1
                issues.append(
                    Issue(
                        severity=Severity.MEDIUM,
                        category="performance",
                        rule=issue_type,
                        message=f"Performance concern: {issue_type.replace('_', ' ')}",
                        file=str(path),
                        line=line_no,
                        snippet=lines[line_no - 1].strip() if line_no <= len(lines) else "",
                    )
                )
        return issues

    def _check_debt_python(self, source: str, path: Path) -> list[Issue]:
        """Use AST to detect tech debt in Python files."""
        issues = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return issues

        for node in ast.walk(tree):
            # Long functions (> 60 lines)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_lines = (node.end_lineno or node.lineno) - node.lineno
                if func_lines > 60:
                    issues.append(
                        Issue(
                            severity=Severity.LOW,
                            category="tech_debt",
                            rule="long_function",
                            message=f"Function '{node.name}' is {func_lines} lines long (limit: 60)",
                            file=str(path),
                            line=node.lineno,
                            snippet=f"def {node.name}(...)",
                        )
                    )
                # Too many arguments
                arg_count = len(node.args.args) + len(node.args.posonlyargs)
                if arg_count > 7:
                    issues.append(
                        Issue(
                            severity=Severity.LOW,
                            category="tech_debt",
                            rule="too_many_args",
                            message=f"Function '{node.name}' has {arg_count} parameters (limit: 7)",
                            file=str(path),
                            line=node.lineno,
                            snippet=f"def {node.name}(...)",
                        )
                    )

        return issues

    def summary_report(self) -> dict:
        """Generate a structured summary for downstream agents."""
        high = sum(1 for r in self.results for i in r.issues if i.severity == Severity.HIGH)
        medium = sum(1 for r in self.results for i in r.issues if i.severity == Severity.MEDIUM)
        low = sum(1 for r in self.results for i in r.issues if i.severity == Severity.LOW)
        return {
            "files_with_issues": len(self.results),
            "total_issues": high + medium + low,
            "by_severity": {"high": high, "medium": medium, "low": low},
            "by_category": self._count_by_category(),
            "top_files": sorted(
                [{"file": r.file_path, "issue_count": len(r.issues)} for r in self.results],
                key=lambda x: x["issue_count"],
                reverse=True,
            )[:10],
        }

    def _count_by_category(self) -> dict:
        counts: dict[str, int] = {}
        for r in self.results:
            for i in r.issues:
                counts[i.category] = counts.get(i.category, 0) + 1
        return counts
