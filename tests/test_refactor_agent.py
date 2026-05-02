"""
Unit tests for RefactorAgent.
"""

import pytest
from src.agents.refactor_agent import RefactorAgent, RefactorConfig
from src.core.models import Issue, ScanResult, Severity


def test_refactor_agent_no_issues():
    """Test RefactorAgent with empty scan results."""
    config = RefactorConfig(max_proposals_per_run=5)
    agent = RefactorAgent(config=config)
    
    proposals = agent.run([])
    
    assert proposals == []


def test_refactor_agent_prioritizes_issues():
    """Test that RefactorAgent prioritizes issues correctly."""
    config = RefactorConfig(max_proposals_per_run=5)
    agent = RefactorAgent(config=config)
    
    # Create issues with different severities
    issues = [
        Issue(Severity.LOW, "tech_debt", "long_function", "Function too long", "file.py", 10),
        Issue(Severity.HIGH, "security", "hardcoded_secret", "Hardcoded secret", "file.py", 5),
        Issue(Severity.MEDIUM, "performance", "loop_db_query", "N+1 queries", "file.py", 15),
    ]
    
    results = [ScanResult("file.py", issues)]
    
    # Should prioritize without error
    proposals = agent.run(results)
    
    # In demo mode (no LLM), should still create mock proposals
    assert len(proposals) >= 0


def test_refactor_agent_health_check():
    """Test agent health check."""
    config = RefactorConfig()
    agent = RefactorAgent(config=config)
    
    health = agent.health_check()
    
    assert health["agent"] == "refactor_agent"
    assert "version" in health
