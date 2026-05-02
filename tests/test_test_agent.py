"""
Unit tests for TestAgent.
"""

import pytest
from src.agents.test_agent import TestAgent, TestConfig
from src.core.models import RefactorProposal, Issue, Severity


def test_test_agent_integration_tests():
    """Test that TestAgent can generate integration tests."""
    config = TestConfig()
    agent = TestAgent(config=config)
    
    proposals = [
        RefactorProposal(
            title="Fix hardcoded password",
            description="Remove hardcoded credentials",
            effort="S",
            changes=[{"file": "auth.py", "line": 10, "original": "", "replacement": ""}],
            source_issues=[],
        )
    ]
    
    suites = agent.run(proposals)
    
    # Should at least generate integration tests
    assert len(suites) >= 1


def test_test_agent_health_check():
    """Test agent health check."""
    config = TestConfig()
    agent = TestAgent(config=config)
    
    health = agent.health_check()
    
    assert health["agent"] == "test_agent"
    assert "version" in health
