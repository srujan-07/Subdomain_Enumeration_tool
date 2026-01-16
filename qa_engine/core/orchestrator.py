"""Main QA scan orchestrator that ties all components together."""

import asyncio
import logging
from typing import Dict, Set

from .crawler import Crawler
from .url_validator import URLValidator
from .browser_analyzer import BrowserAnalyzer
from .structure_detector import StructureDetector
from .page_classifier import PageClassifier
from .issue_detector import IssueDetector
from .scorer import Scorer
from .graph_builder import GraphBuilder
from .events import event_bus, create_event, EventType

logger = logging.getLogger(__name__)


class QAOrchestrator:
    """Orchestrate complete QA analysis pipeline."""

    def __init__(
        self,
        base_url: str,
        max_pages: int = 100,
        http_timeout: int = 10,
        browser_timeout: int = 15,
        crawler_concurrency: int = 10,
        validator_concurrency: int = 20,
        browser_concurrency: int = 5,
        headless: bool = True,
    ) -> None:
        self.base_url = base_url
        self.max_pages = max_pages
        self.http_timeout = http_timeout
        self.browser_timeout = browser_timeout
        self.crawler_concurrency = crawler_concurrency
        self.validator_concurrency = validator_concurrency
        self.browser_concurrency = browser_concurrency
        self.headless = headless

        # Initialize components
        self.crawler = Crawler(
            base_url,
            max_pages=max_pages,
            concurrency=crawler_concurrency,
            timeout=http_timeout,
        )
        self.validator = URLValidator(
            timeout=http_timeout, concurrency=validator_concurrency
        )
        self.structure_detector = StructureDetector(base_url)
        self.classifier = PageClassifier()
        self.issue_detector = IssueDetector()
        self.scorer = Scorer()
        self.graph = GraphBuilder()

    async def run(self, scan_id: str) -> Dict:
        """
        Execute complete QA pipeline.

        Returns:
            {pages: [...], summary: {...}}
        """
        try:
            # Emit scan started
            await event_bus.emit(
                create_event(
                    EventType.SCAN_STARTED,
                    scan_id,
                    {"base_url": self.base_url},
                )
            )

            # Phase 1: Crawl URLs
            logger.info(f"[{scan_id}] Starting crawl")
            crawled = await self.crawler.crawl()
            logger.info(
                f"[{scan_id}] Crawl complete: {len(crawled)} URLs discovered"
            )

            # Emit URL discovered events
            for url in crawled.keys():
                await event_bus.emit(
                    create_event(
                        EventType.URL_DISCOVERED,
                        scan_id,
                        {"url": url},
                    )
                )

            # Phase 2: Validate URLs (HTTP 200 only)
            logger.info(f"[{scan_id}] Validating URLs")
            validation_results = await self.validator.validate_batch(
                list(crawled.keys())
            )
            valid_urls = self.validator.filter_valid_urls(validation_results)
            logger.info(f"[{scan_id}] Validation complete: {len(valid_urls)} HTTP 200")

            # Emit URL validated events
            for url, result in validation_results.items():
                await event_bus.emit(
                    create_event(
                        EventType.URL_VALIDATED,
                        scan_id,
                        {"url": url, "status": result.get("status"), "valid": result.get("valid")},
                    )
                )

            # Phase 3: Browser testing and analysis
            logger.info(f"[{scan_id}] Starting browser testing")
            page_results = await self._test_pages_in_browser(scan_id, valid_urls, crawled)

            # Emit scan completed
            summary = {
                "total_discovered": len(crawled),
                "total_valid": len(valid_urls),
                "total_analyzed": len(page_results),
                "avg_score": (
                    sum(p.get("score", 0) for p in page_results) / len(page_results)
                    if page_results
                    else 0
                ),
            }

            await event_bus.emit(
                create_event(
                    EventType.SCAN_COMPLETED,
                    scan_id,
                    summary,
                )
            )

            logger.info(f"[{scan_id}] QA scan complete")

            return {
                "pages": page_results,
                "summary": summary,
                "graph": self.graph.to_report(),
            }

        except Exception as e:
            logger.exception(f"[{scan_id}] QA scan failed")
            await event_bus.emit(
                create_event(
                    EventType.SCAN_FAILED,
                    scan_id,
                    {"error": str(e)},
                )
            )
            raise

    async def _test_pages_in_browser(
        self, scan_id: str, urls: Set[str], crawled: Dict
    ) -> list:
        """Test each HTTP 200 URL in browser."""
        page_results = []
        sem = asyncio.Semaphore(self.browser_concurrency)

        async def test_single(url: str) -> Dict:
            async with sem:
                return await self._analyze_single_page(scan_id, url, crawled)

        tasks = [test_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Failed to analyze page: {result}")
            else:
                page_results.append(result)
                self.graph.add_page(
                    result["url"], result["page_type"], result["score"]
                )
                self.graph.add_issues(result["url"], result["issues"])

        return page_results

    async def _analyze_single_page(
        self, scan_id: str, url: str, crawled: Dict
    ) -> Dict:
        """Analyze a single page with all detectors."""
        await event_bus.emit(
            create_event(
                EventType.PAGE_TESTING_STARTED,
                scan_id,
                {"url": url},
            )
        )

        html = crawled.get(url, {}).get("html", "")

        async with BrowserAnalyzer(
            timeout=self.browser_timeout, headless=self.headless
        ) as analyzer:
            # Capture runtime data
            runtime_data = await analyzer.analyze(url)

            # Detect structure
            structure = self.structure_detector.analyze(url, html)

            # Classify page type
            page_type = self.classifier.classify(
                html, runtime_data.get("dom_metrics", {})
            )

            # Detect issues
            page_data = {
                **runtime_data,
                "structure": structure,
                "raw_html": html,
            }
            issues = self.issue_detector.detect(page_data)

            # Score page
            score = self.scorer.score_page(issues)

            result = {
                "url": url,
                "page_type": page_type,
                "score": score,
                "issues": issues,
                "structure": structure,
                "dom_metrics": runtime_data.get("dom_metrics", {}),
                "console_logs": runtime_data.get("console_logs", []),
                "network_failures": runtime_data.get("network_failures", []),
                "performance": runtime_data.get("performance", {}),
                "critical_issue_count": sum(
                    1 for i in issues if i.get("severity") in {"critical", "high"}
                ),
                "total_issue_count": len(issues),
            }

            await event_bus.emit(
                create_event(
                    EventType.PAGE_ANALYZED,
                    scan_id,
                    {
                        "url": url,
                        "page_type": page_type,
                        "score": score,
                    },
                )
            )

            return result
