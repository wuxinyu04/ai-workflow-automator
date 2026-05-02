"""
Unit tests for DocAgent.
"""

import pytest
from pathlib import Path
from src.agents.doc_agent import DocAgent, DocConfig
from src.core.models import RefactorProposal


def test_doc_agent_generates_changelog(tmp_path):
    """Test that DocAgent generates changelog entries."""
    config = DocConfig(
        docs_root=str(tmp_path / "docs"),
        api_docs_dir=str(tmp_path / "docs" / "api"),
        changelog_file=str(tmp_path / "CHANGELOG.md"),
    )
    agent = DocAgent(config=config)
    
    proposals = [
        RefactorProposal(
            title="fix: remove hardcoded secret",
            description="Extracted credentials to env vars",
            effort="S",
            changes=[],
            source_issues=[],
        )
    ]
    
    updates = agent.run(proposals, version="1.0.0")
    
    assert any(u.doc_type == "changelog" for u in updates)


def test_doc_agent_health_check():
    """Test agent health check."""
    config = DocConfig()
    agent = DocAgent(config=config)
    
    health = agent.health_check()
    
    assert health["agent"] == "doc_agent"
    assert "version" in health
