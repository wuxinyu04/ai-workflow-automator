#!/usr/bin/env python3
"""
Example 2: Scan-Only Mode
Demonstrates running just the ScanAgent for code analysis.
"""

from src.agents.scan_agent import ScanAgent, ScanConfig


def main():
    # Configure the scanner
    config = ScanConfig(
        target_path="./examples/sample_project",
        include_patterns=["*.py"],
        exclude_dirs=[".git", "node_modules", "__pycache__"],
        enable_security_scan=True,
        enable_perf_scan=True,
        enable_debt_scan=True,
    )

    # Run the scanner
    agent = ScanAgent(config=config)
    results = agent.run()

    # Print summary
    summary = agent.summary_report()
    print("\n" + "="*70)
    print("Code Scan Report:")
    print("="*70)
    print(f"Files with issues: {summary['files_with_issues']}")
    print(f"Total issues: {summary['total_issues']}")
    print(f"\nBy Severity:")
    for sev, count in summary['by_severity'].items():
        print(f"  {sev}: {count}")
    print(f"\nBy Category:")
    for cat, count in summary['by_category'].items():
        print(f"  {cat}: {count}")
    print(f"\nTop Files:")
    for file_info in summary['top_files']:
        print(f"  {file_info['file']}: {file_info['issue_count']} issues")


if __name__ == "__main__":
    main()
