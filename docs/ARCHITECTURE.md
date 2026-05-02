# Architecture

## System Design

### Agent-Based Pipeline

AI Workflow Automator uses an **agent-based architecture** where each phase is handled by a specialized agent:

```
ScanAgent → RefactorAgent → TestAgent → DocAgent
   ↓            ↓              ↓           ↓
Issues    Proposals        TestSuites  DocUpdates
```

### Agent Interface

All agents implement `BaseAgent`:

```python
class BaseAgent(ABC):
    """Abstract base for all workflow agents."""
    
    AGENT_NAME: str
    VERSION: str
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Execute the agent's primary task."""
        ...
    
    def health_check(self) -> dict:
        """Return agent status and version."""
        ...
```

## Data Flow

### Phase 1: ScanAgent

**Input**: File system path  
**Output**: List of `ScanResult` objects

```python
@dataclass
class Issue:
    severity: Severity        # HIGH | MEDIUM | LOW
    category: str             # security | performance | tech_debt
    rule: str                 # Specific rule identifier
    message: str              # Human-readable message
    file: str                 # Relative path
    line: int                 # Line number
    snippet: str              # Code snippet
```

**Detects:**
- Security: hardcoded secrets, SQL injection, eval usage, shell injection
- Performance: N+1 queries, synchronous sleep, nested comprehensions
- Tech Debt: long functions, too many parameters

### Phase 2: RefactorAgent

**Input**: List of `ScanResult`  
**Output**: List of `RefactorProposal`

```python
@dataclass
class RefactorProposal:
    title: str                # PR title
    description: str          # Why this matters
    effort: str               # S | M | L | XL
    changes: list[dict]       # {file, line, original, replacement, explanation}
    source_issues: list[Issue]
```

**Process:**
1. Prioritize issues by severity and impact
2. Group related issues
3. Use LLM to generate refactoring suggestions
4. Output before/after code with explanations

### Phase 3: TestAgent

**Input**: List of `RefactorProposal`  
**Output**: List of `TestSuite`

```python
@dataclass
class TestSuite:
    name: str                 # test_module_name
    source_file: str          # Original source file
    output_file: str          # Where to write tests
    test_cases: list[TestCase]

@dataclass
class TestCase:
    name: str                 # test_function_name
    function_under_test: str  # Function being tested
    code: str                 # Actual test code
    scenario: str             # happy_path | edge_case | error_case | ...
```

**Generates:**
- Unit tests for each public function
- Edge case coverage (empty, None, boundaries)
- Integration tests for the full pipeline
- Pytest-compatible code

### Phase 4: DocAgent

**Input**: List of `RefactorProposal`  
**Output**: List of `DocUpdate`

```python
@dataclass
class DocUpdate:
    doc_type: str             # api_reference | changelog | readme | docstring
    file: str                 # Path to document
    content: str              # Generated content
    source_proposal: str      # What triggered this update
```

**Produces:**
- API reference pages (Markdown)
- Changelog entries (Keep a Changelog format)
- Updated docstrings (Google style)
- README sections

## LLM Integration

### Supported Providers

- **MiMo**: Long-context model (128k tokens) - default
- **Claude**: Anthropic's Claude 3.5 Sonnet
- **OpenAI**: GPT-4 / GPT-4 Turbo (future)

### MiMo Advantages

- **128k context window** enables processing entire modules without chunking
- **Lower costs** for long-context tasks
- **Specialized for code** with Code understanding
- **Rate limiting friendly** for batch processing

### Token Usage

Typical per-phase consumption:

| Phase | Tokens | LLM Required |
|-------|--------|--------------|
| Scan | 0 | No |
| Refactor | 1-2M | Yes |
| Test | 0.5-1.5M | Yes |
| Doc | 0.3-0.8M | Yes |

## Configuration

Pipeline behavior is configured via:

1. **YAML Configuration** (`config.yaml`)
2. **CLI Arguments** (overrides YAML)
3. **Environment Variables** (e.g., `MIMO_API_KEY`)

### Priority (highest to lowest):
1. CLI arguments
2. Environment variables
3. YAML config
4. Hardcoded defaults

## Error Handling

### Graceful Degradation

- Missing LLM key → Run scan-only (Phase 1)
- LLM rate limit → Retry with backoff
- Syntax error in scanned file → Log warning, continue
- Invalid proposal format → Skip proposal, continue

### Logging

Structured logging with levels:
- DEBUG: Detailed execution traces
- INFO: Phase progress and summaries
- WARNING: Recoverable errors
- ERROR: Unrecoverable failures

## Performance Characteristics

- **Scan Phase**: O(n) where n = number of files
- **Refactor Phase**: O(m log m) where m = number of issues (due to sorting)
- **Test Phase**: O(f) where f = number of functions
- **Doc Phase**: O(p) where p = number of proposals

Typical project (1000 files, 100 issues):
- Scan: ~2s
- Refactor + LLM: ~45-90s (LLM dependent)
- Test + LLM: ~30-60s (LLM dependent)
- Doc + LLM: ~15-30s (LLM dependent)
- **Total**: ~1-3 minutes

## Extensibility

### Adding New Agents

Inherit from `BaseAgent`:

```python
from src.core.base_agent import BaseAgent

class MyAgent(BaseAgent):
    AGENT_NAME = "my_agent"
    VERSION = "0.1.0"
    
    def __init__(self, config, llm_client=None):
        super().__init__(llm_client=llm_client)
        self.config = config
    
    def run(self, input_data):
        # Implementation
        return output_data
```

### Adding New Security Rules

Update `SECURITY_PATTERNS` in `ScanAgent`:

```python
SECURITY_PATTERNS = {
    "my_rule": re.compile(r"pattern_to_detect"),
}
```

## Testing Strategy

- **Unit tests**: Each agent independently
- **Integration tests**: Full pipeline on sample project
- **Property tests**: Hypothesis-based fuzzing (future)
- **Regression tests**: Known issues database

Run tests:
```bash
pytest tests/ -v --cov=src
```

---

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.
