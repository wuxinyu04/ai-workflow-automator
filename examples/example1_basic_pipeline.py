#!/usr/bin/env python3
"""
Example 1: Basic Pipeline Run
Demonstrates running the full 4-phase pipeline on a target codebase.
"""

from src.pipeline import Pipeline, PipelineConfig


def main():
    # Configure the pipeline
    config = PipelineConfig(
        target_path="./examples/sample_project",  # Path to analyze
        output_dir="./awa_output",
        version="1.0.0",
        llm_provider="mimo",                      # Use MiMo for long context
        # llm_api_key="sk-your-key-here",        # Or set AWA_LLM_API_KEY env var
        dry_run=False,                            # Set True for scan-only mode
    )

    # Run the pipeline
    pipeline = Pipeline(config)
    result = pipeline.run()

    # Print results
    import json
    print("\n" + "="*70)
    print("Pipeline Results:")
    print("="*70)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
