# Contributing Guide

## Getting Started

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/ai-workflow-automator.git
   cd ai-workflow-automator
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Run tests**
   ```bash
   pytest tests/
   ```

## Architecture

### Agent Pattern

All agents inherit from `BaseAgent` and implement:

```python
class MyAgent(BaseAgent):
    AGENT_NAME = "my_agent"
    VERSION = "0.1.0"
    
    def run(self, *args, **kwargs) -> Any:
        """Main execution method."""
        pass
```

### Data Flow

- **ScanResult**: Issues detected in a file
- **RefactorProposal**: Suggested code changes
- **TestSuite**: Generated test cases
- **DocUpdate**: Documentation changes

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes with tests
3. Run linting: `ruff check src/`
4. Run type checking: `mypy src/`
5. Open a PR with description

## Code Style

- **Python 3.11+** only
- **100-char line limit** (configurable in ruff)
- **Type hints** for all public APIs
- **Docstrings** in Google style

Example:
```python
def process_data(items: List[str], multiplier: int = 2) -> Dict[str, Any]:
    """
    Process items and return results.
    
    Args:
        items: List of strings to process
        multiplier: Factor to multiply counts by
        
    Returns:
        Dictionary with processed results
        
    Raises:
        ValueError: If multiplier is negative
    """
    if multiplier < 0:
        raise ValueError("multiplier must be non-negative")
    return {"count": len(items) * multiplier}
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_scan_agent.py

# Run with coverage
pytest --cov=src tests/
```

## Releasing

1. Update version in `pyproject.toml` and `src/__init__.py`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v0.3.2`
4. Push: `git push origin v0.3.2`
5. Publish to PyPI (CI/CD handles this)

---

Questions? Open an issue on GitHub!
