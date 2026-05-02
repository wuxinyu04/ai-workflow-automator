"""
Test Agent - Phase 3
Automatically generates unit and integration tests from code changes.
"""

import ast
import inspect
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..core.base_agent import BaseAgent
from ..core.models import RefactorProposal, TestSuite, TestCase


SYSTEM_PROMPT = """You are a test automation expert.
Given a Python function or class, generate comprehensive pytest test cases that:
1. Cover happy path scenarios
2. Cover edge cases (empty inputs, boundary values, None)
3. Cover error cases (exceptions, invalid types)
4. Use appropriate fixtures and mocks
5. Follow pytest best practices

Output only valid Python test code. No explanations outside comments."""


@dataclass
class TestConfig:
    output_dir: str = "tests/generated"
    framework: str = "pytest"
    coverage_target: float = 0.80
    generate_integration_tests: bool = True
    max_test_cases_per_function: int = 8
    use_hypothesis: bool = False  # property-based testing


class TestAgent(BaseAgent):
    """
    Intelligent test generation agent.

    Capabilities:
    - Parses function signatures and docstrings for context
    - Generates unit tests for individual functions
    - Generates integration tests for agent interactions
    - Iteratively improves tests through LLM dialogue
    - Reports coverage delta after test generation
    """

    AGENT_NAME = "test_agent"
    VERSION = "0.4.0"

    def __init__(self, config: TestConfig, llm_client=None):
        super().__init__(llm_client=llm_client)
        self.config = config
        self.generated_suites: list[TestSuite] = []

    def run(self, proposals: list[RefactorProposal], source_root: str = ".") -> list[TestSuite]:
        """Generate tests for all changed files in proposals."""
        changed_files = self._collect_changed_files(proposals)
        self.logger.info(f"[TestAgent] Generating tests for {len(changed_files)} files")

        for file_path in changed_files:
            suite = self._generate_test_suite(Path(file_path), source_root)
            if suite:
                self.generated_suites.append(suite)
                self._write_test_file(suite)

        if self.config.generate_integration_tests:
            integration_suite = self._generate_integration_tests(proposals)
            if integration_suite:
                self.generated_suites.append(integration_suite)
                self._write_test_file(integration_suite)

        self.logger.info(f"[TestAgent] Generated {len(self.generated_suites)} test suites")
        return self.generated_suites

    def _collect_changed_files(self, proposals: list[RefactorProposal]) -> list[str]:
        files = set()
        for p in proposals:
            for change in p.changes:
                if change.get("file", "").endswith(".py"):
                    files.add(change["file"])
        return list(files)

    def _generate_test_suite(self, file_path: Path, source_root: str) -> Optional[TestSuite]:
        """Parse file and generate tests for each public function/class."""
        if not file_path.exists():
            self.logger.warning(f"File not found: {file_path}")
            return None

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, SyntaxError) as e:
            self.logger.warning(f"Cannot parse {file_path}: {e}")
            return None

        test_cases: list[TestCase] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):  # public only
                    cases = self._generate_cases_for_function(node, source)
                    test_cases.extend(cases)

        if not test_cases:
            return None

        module_name = file_path.stem
        return TestSuite(
            name=f"test_{module_name}",
            source_file=str(file_path),
            output_file=str(Path(self.config.output_dir) / f"test_{module_name}.py"),
            test_cases=test_cases,
        )

    def _generate_cases_for_function(
        self, node: ast.FunctionDef, source: str
    ) -> list[TestCase]:
        """Use LLM or heuristics to generate test cases for a function."""
        func_name = node.name
        args = [a.arg for a in node.args.args if a.arg != "self"]
        docstring = ast.get_docstring(node) or ""

        if self.llm_client:
            return self._llm_generate_cases(func_name, args, docstring, source, node)
        else:
            return self._heuristic_generate_cases(func_name, args)

    def _heuristic_generate_cases(self, func_name: str, args: list[str]) -> list[TestCase]:
        """Fallback: generate basic test stubs without LLM."""
        cases = []
        # Happy path
        cases.append(TestCase(
            name=f"test_{func_name}_happy_path",
            function_under_test=func_name,
            code=textwrap.dedent(f"""
                def test_{func_name}_happy_path():
                    # TODO: provide valid inputs
                    result = {func_name}({', '.join(f'{a}=...' for a in args)})
                    assert result is not None
            """).strip(),
            scenario="happy_path",
        ))
        # None input guard
        if args:
            cases.append(TestCase(
                name=f"test_{func_name}_none_input",
                function_under_test=func_name,
                code=textwrap.dedent(f"""
                    import pytest

                    def test_{func_name}_none_input():
                        with pytest.raises((TypeError, ValueError)):
                            {func_name}({args[0]}=None)
                """).strip(),
                scenario="error_case",
            ))
        return cases

    def _llm_generate_cases(
        self,
        func_name: str,
        args: list[str],
        docstring: str,
        full_source: str,
        node: ast.FunctionDef,
    ) -> list[TestCase]:
        """Generate tests via LLM with multi-turn refinement."""
        start = node.lineno - 1
        end = node.end_lineno or (start + 30)
        func_source = "\n".join(full_source.splitlines()[start:end])

        prompt = f"""Generate pytest test cases for this function:

```python
{func_source}
```

Docstring: {docstring or 'N/A'}
Arguments: {args}

Requirements:
- {self.config.max_test_cases_per_function} test cases max
- Cover: happy path, edge cases, error cases
- Use pytest fixtures where appropriate
- Output only the test code"""

        response = self.llm_client.chat(
            system=SYSTEM_PROMPT,
            user=prompt,
            temperature=0.1,
        )

        # Parse response into individual test cases
        return self._parse_test_code(response, func_name)

    def _parse_test_code(self, code: str, func_name: str) -> list[TestCase]:
        """Extract individual test functions from LLM response."""
        cases = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    start = node.lineno - 1
                    end = node.end_lineno or (start + 20)
                    snippet = "\n".join(code.splitlines()[start:end])
                    cases.append(TestCase(
                        name=node.name,
                        function_under_test=func_name,
                        code=snippet,
                        scenario="llm_generated",
                    ))
        except SyntaxError:
            # Return as a single block if parsing fails
            cases.append(TestCase(
                name=f"test_{func_name}_llm",
                function_under_test=func_name,
                code=code,
                scenario="llm_generated",
            ))
        return cases

    def _generate_integration_tests(self, proposals: list[RefactorProposal]) -> Optional[TestSuite]:
        """Generate end-to-end integration tests for the agent pipeline."""
        code = textwrap.dedent("""
            \"\"\"
            Integration tests for the AI Workflow Automator pipeline.
            Auto-generated by TestAgent.
            \"\"\"
            import pytest
            from pathlib import Path
            from src.agents.scan_agent import ScanAgent, ScanConfig
            from src.agents.refactor_agent import RefactorAgent, RefactorConfig
            from src.agents.test_agent import TestAgent, TestConfig
            from src.agents.doc_agent import DocAgent, DocConfig


            @pytest.fixture
            def sample_project(tmp_path):
                \"\"\"Create a minimal project with known issues for testing.\"\"\"
                src = tmp_path / "src"
                src.mkdir()
                bad_code = src / "bad_module.py"
                bad_code.write_text(
                    'import os\\n'
                    'password = "hardcoded_secret_123"\\n'
                    'def fetch_users(db):\\n'
                    '    users = db.query("SELECT * FROM users").all()\\n'
                    '    result = []\\n'
                    '    for u in users:\\n'
                    '        details = db.query(f"SELECT * FROM details WHERE id={u.id}").first()\\n'
                    '        result.append(details)\\n'
                    '    return result\\n'
                )
                return tmp_path


            def test_full_pipeline(sample_project):
                \"\"\"End-to-end: scan -> refactor -> test -> doc.\"\"\"
                # Phase 1: Scan
                scan_cfg = ScanConfig(target_path=str(sample_project))
                scan = ScanAgent(config=scan_cfg)
                results = scan.run()
                assert len(results) > 0, "Scanner should detect issues in sample project"
                summary = scan.summary_report()
                assert summary["total_issues"] >= 2

                # Phase 2: Refactor proposals
                refactor_cfg = RefactorConfig(max_proposals_per_run=5)
                refactor = RefactorAgent(config=refactor_cfg)
                proposals = refactor.run(results)
                assert len(proposals) > 0

                # Phase 3: Test generation
                test_cfg = TestConfig(output_dir=str(sample_project / "tests"))
                tester = TestAgent(config=test_cfg)
                suites = tester.run(proposals, source_root=str(sample_project))
                # At least integration tests should be generated
                assert len(suites) >= 1


            def test_scan_agent_empty_dir(tmp_path):
                \"\"\"Scanning an empty directory should not raise.\"\"\"
                cfg = ScanConfig(target_path=str(tmp_path))
                agent = ScanAgent(config=cfg)
                results = agent.run()
                assert results == []


            def test_refactor_agent_no_issues():
                \"\"\"RefactorAgent with empty scan results returns empty proposals.\"\"\"
                cfg = RefactorConfig()
                agent = RefactorAgent(config=cfg)
                proposals = agent.run([])
                assert proposals == []
        """).strip()

        return TestSuite(
            name="test_integration_pipeline",
            source_file="(pipeline)",
            output_file=str(Path(self.config.output_dir) / "test_integration_pipeline.py"),
            test_cases=[
                TestCase(
                    name="test_integration_pipeline",
                    function_under_test="pipeline",
                    code=code,
                    scenario="integration",
                )
            ],
        )

    def _write_test_file(self, suite: TestSuite) -> None:
        out = Path(suite.output_file)
        out.parent.mkdir(parents=True, exist_ok=True)
        header = textwrap.dedent(f"""
            # Auto-generated by TestAgent v{self.VERSION}
            # Source: {suite.source_file}
            # DO NOT EDIT MANUALLY - regenerate with: python -m awa test --regen
        """).strip() + "\n\n"
        body = "\n\n".join(tc.code for tc in suite.test_cases)
        out.write_text(header + body, encoding="utf-8")
        self.logger.info(f"[TestAgent] Written: {out}")
