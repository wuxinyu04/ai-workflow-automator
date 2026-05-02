# Examples

This directory contains example scripts and a sample project for testing the AI Workflow Automator.

## Scripts

### Example 1: Basic Pipeline Run

```bash
python examples/example1_basic_pipeline.py
```

Demonstrates the full 4-phase pipeline on the sample project.

### Example 2: Scan-Only Mode

```bash
python examples/example2_scan_only.py
```

Shows how to run just the ScanAgent for code analysis without LLM.

## Sample Project

The `sample_project/` directory contains:

- `bad_module.py`: Intentionally includes issues (security, perf, debt)
- `good_module.py`: Well-written code for comparison

### Running on Sample Project

```bash
# Scan for issues
python main.py scan --target ./examples/sample_project

# Full pipeline (demo mode - no LLM)
python main.py run --target ./examples/sample_project --dry-run

# Full pipeline with LLM
python main.py run \
  --target ./examples/sample_project \
  --provider mimo \
  --api-key $MIMO_API_KEY
```

## Expected Output

When scanning the sample project:

```
[ScanAgent] Found 2 files to scan
[ScanAgent] Scan complete. 1 files with issues, 8 total issues found.

Issues Summary:
- 2 HIGH (security)
- 3 MEDIUM (performance)
- 3 LOW (tech_debt)
```

Issues found:
1. Hardcoded password in `bad_module.py` line 8
2. SQL injection risk in `bad_module.py` line 35
3. N+1 query pattern in `bad_module.py` lines 18-22
4. Long function (>60 lines) in `bad_module.py` lines 66-90
5. Too many parameters (8) in `bad_module.py` line 13

## Creating Your Own Example

```python
from src.pipeline import Pipeline, PipelineConfig

config = PipelineConfig(
    target_path="./my_project",
    output_dir="./awa_output",
    llm_provider="mimo",  # or "claude"
    # llm_api_key="sk-xxx",  # or set AWA_LLM_API_KEY env var
)

pipeline = Pipeline(config)
result = pipeline.run()

import json
print(json.dumps(result, indent=2))
```

See [GETTING_STARTED.md](../docs/GETTING_STARTED.md) for more details.
