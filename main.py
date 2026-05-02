#!/usr/bin/env python3
"""
AI Workflow Automator — CLI entry point.

Usage:
  python -m awa run --target ./my_project
  python -m awa run --target ./my_project --provider mimo --api-key sk-xxx
  python -m awa scan --target ./my_project
"""

import argparse
import json
import sys

from src.pipeline import Pipeline, PipelineConfig


def cmd_run(args):
    config = PipelineConfig(
        target_path=args.target,
        output_dir=args.output,
        version=args.version,
        llm_provider=args.provider,
        llm_api_key=args.api_key,
        llm_base_url=args.base_url,
        dry_run=args.dry_run,
    )
    pipeline = Pipeline(config)
    result = pipeline.run()
    print("\n" + json.dumps(result, indent=2))
    return 0 if result["status"] in ("success", "clean") else 1


def cmd_scan(args):
    from src.agents.scan_agent import ScanAgent, ScanConfig
    cfg = ScanConfig(target_path=args.target)
    agent = ScanAgent(config=cfg)
    results = agent.run()
    report = agent.summary_report()
    print(json.dumps(report, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="awa",
        description="AI Workflow Automator — automated code review, refactoring, testing, and docs",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ── run ────────────────────────────────────────────────────────
    run_p = subparsers.add_parser("run", help="Run the full 4-phase pipeline")
    run_p.add_argument("--target", required=True, help="Path to the codebase to analyze")
    run_p.add_argument("--output", default="awa_output", help="Output directory")
    run_p.add_argument("--version", default="Unreleased", help="Version tag for changelog")
    run_p.add_argument("--provider", default="mimo", choices=["mimo", "claude", "openai"])
    run_p.add_argument("--api-key", default=None, dest="api_key")
    run_p.add_argument("--base-url", default=None, dest="base_url")
    run_p.add_argument("--dry-run", action="store_true", dest="dry_run",
                       help="Scan only, skip refactor/test/doc generation")
    run_p.set_defaults(func=cmd_run)

    # ── scan ───────────────────────────────────────────────────────
    scan_p = subparsers.add_parser("scan", help="Run Phase 1 scan only")
    scan_p.add_argument("--target", required=True)
    scan_p.set_defaults(func=cmd_scan)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
