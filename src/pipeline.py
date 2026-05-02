"""
Pipeline Orchestrator
Coordinates all four agents in sequence with progress reporting.
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional

from .agents.scan_agent import ScanAgent, ScanConfig
from .agents.refactor_agent import RefactorAgent, RefactorConfig
from .agents.test_agent import TestAgent, TestConfig
from .agents.doc_agent import DocAgent, DocConfig


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("awa.pipeline")


@dataclass
class PipelineConfig:
    target_path: str
    output_dir: str = "awa_output"
    version: str = "Unreleased"
    llm_provider: str = "mimo"   # mimo | claude | openai
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    dry_run: bool = False

    # Per-agent overrides
    scan: Optional[ScanConfig] = None
    refactor: Optional[RefactorConfig] = None
    test: Optional[TestConfig] = None
    doc: Optional[DocConfig] = None


class Pipeline:
    """
    Four-phase AI workflow automation pipeline:

      Phase 1 → ScanAgent    : identify issues
      Phase 2 → RefactorAgent: generate proposals
      Phase 3 → TestAgent    : auto-generate tests
      Phase 4 → DocAgent     : sync documentation
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.llm_client = self._init_llm()

    def _init_llm(self):
        """Initialize LLM client based on provider config."""
        if not self.config.llm_api_key:
            logger.warning("No LLM API key provided - running in demo mode (no LLM calls)")
            return None

        provider = self.config.llm_provider.lower()
        if provider == "mimo":
            from .utils.llm_clients import MiMoClient
            return MiMoClient(
                api_key=self.config.llm_api_key,
                base_url=self.config.llm_base_url or "https://api.mimo.ai/v1",
            )
        elif provider == "claude":
            from .utils.llm_clients import ClaudeClient
            return ClaudeClient(api_key=self.config.llm_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def run(self) -> dict:
        """Execute the full pipeline and return a summary report."""
        start_time = time.time()
        logger.info("=" * 60)
        logger.info(f"AI Workflow Automator — Pipeline Start")
        logger.info(f"Target: {self.config.target_path}")
        logger.info(f"Provider: {self.config.llm_provider} | Dry-run: {self.config.dry_run}")
        logger.info("=" * 60)

        # ── Phase 1: Scan ──────────────────────────────────────────
        scan_cfg = self.config.scan or ScanConfig(target_path=self.config.target_path)
        scan_cfg.target_path = self.config.target_path
        scan_agent = ScanAgent(config=scan_cfg, llm_client=self.llm_client)

        logger.info("▶ Phase 1/4 — Code Scan")
        scan_results = scan_agent.run()
        scan_summary = scan_agent.summary_report()
        logger.info(f"  ✓ {scan_summary['total_issues']} issues found in {scan_summary['files_with_issues']} files")

        if not scan_results:
            logger.info("No issues found. Pipeline complete.")
            return {"status": "clean", "scan": scan_summary}

        # ── Phase 2: Refactor ──────────────────────────────────────
        refactor_cfg = self.config.refactor or RefactorConfig()
        refactor_agent = RefactorAgent(config=refactor_cfg, llm_client=self.llm_client)

        logger.info("▶ Phase 2/4 — Refactor Proposals")
        if not self.config.dry_run:
            proposals = refactor_agent.run(scan_results)
        else:
            proposals = []
        logger.info(f"  ✓ {len(proposals)} proposals generated")

        # ── Phase 3: Test ──────────────────────────────────────────
        test_cfg = self.config.test or TestConfig(
            output_dir=f"{self.config.output_dir}/tests"
        )
        test_agent = TestAgent(config=test_cfg, llm_client=self.llm_client)

        logger.info("▶ Phase 3/4 — Test Generation")
        if not self.config.dry_run:
            suites = test_agent.run(proposals, source_root=self.config.target_path)
        else:
            suites = []
        total_cases = sum(len(s.test_cases) for s in suites)
        logger.info(f"  ✓ {len(suites)} suites, {total_cases} test cases generated")

        # ── Phase 4: Documentation ─────────────────────────────────
        doc_cfg = self.config.doc or DocConfig(
            docs_root=f"{self.config.output_dir}/docs",
            api_docs_dir=f"{self.config.output_dir}/docs/api",
            changelog_file=f"{self.config.output_dir}/CHANGELOG.md",
        )
        doc_agent = DocAgent(config=doc_cfg, llm_client=self.llm_client)

        logger.info("▶ Phase 4/4 — Documentation Sync")
        if not self.config.dry_run:
            doc_updates = doc_agent.run(proposals, version=self.config.version)
        else:
            doc_updates = []
        logger.info(f"  ✓ {len(doc_updates)} doc files updated")

        elapsed = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"Pipeline complete in {elapsed:.1f}s")

        return {
            "status": "success",
            "elapsed_seconds": round(elapsed, 2),
            "scan": scan_summary,
            "proposals": len(proposals),
            "test_suites": len(suites),
            "test_cases": total_cases,
            "doc_updates": len(doc_updates),
        }
