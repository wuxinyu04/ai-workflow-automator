"""
Core data models for AI Workflow Automator.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Issue:
    severity: Severity
    category: str  # security | performance | tech_debt
    rule: str
    message: str
    file: str
    line: int
    snippet: str = ""

    def to_dict(self) -> dict:
        return {
            "severity": self.severity.value,
            "category": self.category,
            "rule": self.rule,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "snippet": self.snippet,
        }


@dataclass
class ScanResult:
    file_path: str
    issues: list[Issue] = field(default_factory=list)


@dataclass
class RefactorProposal:
    title: str
    description: str
    effort: str  # S | M | L | XL
    changes: list[dict]
    source_issues: list[Issue] = field(default_factory=list)


@dataclass
class TestCase:
    name: str
    function_under_test: str
    code: str
    scenario: str  # happy_path | edge_case | error_case | integration | llm_generated


@dataclass
class TestSuite:
    name: str
    source_file: str
    output_file: str
    test_cases: list[TestCase] = field(default_factory=list)


@dataclass
class DocUpdate:
    doc_type: str  # api_reference | changelog | readme | docstring
    file: str
    content: str
    source_proposal: str = ""
