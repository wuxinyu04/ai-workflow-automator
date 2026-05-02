"""
Unit tests for the ScanAgent.
"""

import pytest
from pathlib import Path
from src.agents.scan_agent import ScanAgent, ScanConfig
from src.core.models import Severity


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project with known issues."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create a file with known issues
    bad_file = src_dir / "bad_code.py"
    bad_file.write_text("""
import os
password = "hardcoded_secret_123"

def fetch_data(db):
    for item in db.query():
        details = db.query(f"SELECT * FROM details WHERE id={item.id}")
    
    return [x for y in items for x in y for z in y]
""")
    
    return tmp_path


def test_scan_agent_finds_issues(temp_project):
    """Test that ScanAgent detects known issues."""
    config = ScanConfig(target_path=str(temp_project))
    agent = ScanAgent(config=config)
    results = agent.run()
    
    assert len(results) > 0, "Should find issues in bad_code.py"
    
    # Check that security issues are detected
    issues = results[0].issues
    assert any(i.category == "security" for i in issues), "Should detect hardcoded secret"


def test_scan_agent_empty_directory(tmp_path):
    """Test that ScanAgent handles empty directories gracefully."""
    config = ScanConfig(target_path=str(tmp_path))
    agent = ScanAgent(config=config)
    results = agent.run()
    
    assert results == [], "Empty directory should return no results"


def test_scan_agent_summary_report(temp_project):
    """Test that summary_report works correctly."""
    config = ScanConfig(target_path=str(temp_project))
    agent = ScanAgent(config=config)
    agent.run()
    
    summary = agent.summary_report()
    
    assert "total_issues" in summary
    assert "by_severity" in summary
    assert "by_category" in summary
    assert summary["total_issues"] > 0


def test_scan_agent_health_check():
    """Test agent health check."""
    config = ScanConfig(target_path=".")
    agent = ScanAgent(config=config)
    
    health = agent.health_check()
    
    assert health["agent"] == "scan_agent"
    assert "version" in health
    assert health["llm_connected"] is False
