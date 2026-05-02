"""
Pytest configuration and shared fixtures.
"""

import pytest
from pathlib import Path
from src.agents.scan_agent import ScanConfig, ScanAgent
from src.agents.refactor_agent import RefactorConfig, RefactorAgent
from src.agents.test_agent import TestConfig, TestAgent
from src.agents.doc_agent import DocConfig, DocAgent


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file with issues."""
    file = tmp_path / "sample.py"
    file.write_text('''
def long_function_with_many_lines(param1, param2, param3, param4, param5, param6, param7, param8):
    """A function with too many parameters."""
    value = 0
    for i in range(100):
        value += i
        if value > 1000:
            value = 0
    password = "hardcoded_pass"
    return value
''')
    return file


@pytest.fixture
def project_with_issues(tmp_path):
    """Create a minimal project with known issues."""
    src = tmp_path / "src"
    src.mkdir()
    
    bad_module = src / "bad.py"
    bad_module.write_text('''
password = "secret123"

def get_users(db):
    users = db.query("SELECT * FROM users")
    for u in users:
        details = db.query(f"SELECT * FROM details WHERE id={u.id}")
    return users
''')
    
    good_module = src / "good.py"
    good_module.write_text('''
def safe_fetch(item_id: int):
    """Safely fetch item."""
    return {"id": item_id}
''')
    
    return tmp_path


@pytest.fixture
def scan_agent(project_with_issues):
    """Create a ScanAgent instance."""
    config = ScanConfig(target_path=str(project_with_issues))
    return ScanAgent(config=config)


@pytest.fixture
def refactor_agent():
    """Create a RefactorAgent instance."""
    config = RefactorConfig(max_proposals_per_run=5)
    return RefactorAgent(config=config)


@pytest.fixture
def test_agent(tmp_path):
    """Create a TestAgent instance."""
    config = TestConfig(output_dir=str(tmp_path / "tests"))
    return TestAgent(config=config)


@pytest.fixture
def doc_agent(tmp_path):
    """Create a DocAgent instance."""
    config = DocConfig(
        docs_root=str(tmp_path / "docs"),
        api_docs_dir=str(tmp_path / "docs" / "api"),
        changelog_file=str(tmp_path / "CHANGELOG.md"),
    )
    return DocAgent(config=config)
