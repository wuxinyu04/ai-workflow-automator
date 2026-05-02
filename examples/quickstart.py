#!/usr/bin/env python3
"""
Quick Start Script for AI Workflow Automator

This script demonstrates all major features of the system.
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.scan_agent import ScanAgent, ScanConfig
from src.agents.refactor_agent import RefactorAgent, RefactorConfig
from src.agents.test_agent import TestAgent, TestConfig
from src.agents.doc_agent import DocAgent, DocConfig


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def main():
    sample_project = project_root / "examples" / "sample_project"
    
    if not sample_project.exists():
        print(f"Error: Sample project not found at {sample_project}")
        return 1
    
    # Phase 1: Scan
    print_header("Phase 1: Code Scanning")
    print(f"Target: {sample_project}")
    
    scan_cfg = ScanConfig(target_path=str(sample_project))
    scan_agent = ScanAgent(config=scan_cfg)
    scan_results = scan_agent.run()
    
    summary = scan_agent.summary_report()
    print(f"\nResults:")
    print(f"  Files with issues: {summary['files_with_issues']}")
    print(f"  Total issues: {summary['total_issues']}")
    print(f"\n  By Severity:")
    for sev, count in summary['by_severity'].items():
        print(f"    {sev.upper()}: {count}")
    print(f"\n  By Category:")
    for cat, count in summary['by_category'].items():
        print(f"    {cat}: {count}")
    
    print(f"\n  Top Files:")
    for file_info in summary['top_files'][:5]:
        file_name = Path(file_info['file']).name
        print(f"    {file_name}: {file_info['issue_count']} issues")
    
    if not scan_results:
        print("\nNo issues found!")
        return 0
    
    # Phase 2: Refactor (demo mode)
    print_header("Phase 2: Refactoring Proposals (Demo Mode)")
    refactor_cfg = RefactorConfig(max_proposals_per_run=5)
    refactor_agent = RefactorAgent(config=refactor_cfg)
    proposals = refactor_agent.run(scan_results)
    
    print(f"Generated {len(proposals)} proposals:")
    for idx, proposal in enumerate(proposals[:3], 1):
        print(f"\n  {idx}. {proposal.title}")
        print(f"     Effort: {proposal.effort}")
        print(f"     Changes: {len(proposal.changes)}")
    
    if len(proposals) > 3:
        print(f"\n  ... and {len(proposals) - 3} more proposals")
    
    # Phase 3: Test Generation (demo mode)
    print_header("Phase 3: Test Generation (Demo Mode)")
    test_cfg = TestConfig(output_dir=str(project_root / "awa_output" / "tests"))
    test_agent = TestAgent(config=test_cfg)
    suites = test_agent.run(proposals, source_root=str(sample_project))
    
    total_cases = sum(len(s.test_cases) for s in suites)
    print(f"Generated {len(suites)} test suites with {total_cases} test cases")
    
    # Phase 4: Documentation (demo mode)
    print_header("Phase 4: Documentation Sync (Demo Mode)")
    doc_cfg = DocConfig(
        docs_root=str(project_root / "awa_output" / "docs"),
        api_docs_dir=str(project_root / "awa_output" / "docs" / "api"),
        changelog_file=str(project_root / "awa_output" / "CHANGELOG.md"),
    )
    doc_agent = DocAgent(config=doc_cfg)
    doc_updates = doc_agent.run(proposals, version="1.0.0")
    
    print(f"Generated {len(doc_updates)} documentation updates")
    
    # Summary
    print_header("Pipeline Summary")
    results = {
        "status": "success",
        "scan": {
            "files_scanned": len(scan_results),
            "total_issues": summary['total_issues'],
        },
        "refactor": {
            "proposals": len(proposals),
        },
        "test": {
            "suites": len(suites),
            "cases": total_cases,
        },
        "doc": {
            "updates": len(doc_updates),
        },
    }
    
    print(json.dumps(results, indent=2))
    
    print_header("Next Steps")
    print("""
1. Review the scan results above
2. Run: python main.py scan --target <your_project>
3. For full pipeline with LLM:
   
   export MIMO_API_KEY=sk-your-key
   python main.py run --target <your_project> --provider mimo

4. Check documentation:
   - docs/GETTING_STARTED.md
   - docs/ARCHITECTURE.md
   - examples/README.md
""")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
