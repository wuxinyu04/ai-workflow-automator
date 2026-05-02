# Getting Started with AI Workflow Automator

## Prerequisites

- Python 3.11+
- pip

## Installation

### From GitHub (Development)

```bash
git clone https://github.com/yourusername/ai-workflow-automator.git
cd ai-workflow-automator
pip install -r requirements.txt
```

### From PyPI (Production)

```bash
pip install ai-workflow-automator
```

## Quick Start

### 1. Demo Mode (No API Key)

Scan your codebase without LLM:

```bash
python main.py scan --target ./my_project
```

### 2. With MiMo API

Full pipeline with AI-assisted refactoring:

```bash
export MIMO_API_KEY=sk-your-key-here
python main.py run --target ./my_project --provider mimo
```

### 3. With Anthropic Claude

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key
python main.py run --target ./my_project --provider claude
```

## Configuration

Create `config.yaml`:

```yaml
llm:
  provider: mimo
  base_url: https://api.mimo.ai/v1

phases:
  scan:
    enable: true
    include_patterns: ["*.py", "*.ts"]
  refactor:
    max_proposals_per_run: 10
  test:
    coverage_target: 0.80
  doc:
    auto_update_changelog: true
```

## Output

Results are saved to `awa_output/`:

```
awa_output/
├── CHANGELOG.md           # Updated changelog
├── docs/api/              # Per-module API docs
└── tests/generated/       # Generated test suites
```

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for design details
- See [EXAMPLES.md](EXAMPLES.md) for real-world use cases
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute
