"""Autonomous AI-driven web testing engine orchestrator."""

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict

from core import (
    Crawler,
    BrowserAnalyzer,
    StructureDetector,
    PageClassifier,
    IssueDetector,
    GraphBuilder,
    Scorer,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("qa-engine")


async def process_page(
    url: str,
    html: str,
    analyzer: BrowserAnalyzer,
    structure_detector: StructureDetector,
    classifier: PageClassifier,
    issue_detector: IssueDetector,
    scorer: Scorer,
) -> Dict:
    structure = structure_detector.analyze(url, html)
    runtime_data = await analyzer.analyze(url)

    page_data = {**runtime_data, "structure": structure, "raw_html": html}

    page_type = classifier.classify(html, runtime_data.get("dom_metrics", {}))
    page_data["page_type"] = page_type

    issues = issue_detector.detect(page_data)
    score = scorer.score_page(issues)

    return {
        "url": url,
        "page_type": page_type,
        "issues": issues,
        "score": score,
        "structure": structure,
        "performance": runtime_data.get("performance", {}),
        "dom_metrics": runtime_data.get("dom_metrics", {}),
        "console_logs": runtime_data.get("console_logs", []),
        "network_failures": runtime_data.get("network_failures", []),
    }


async def run(args) -> Dict:
    logger.info("Starting crawl: %s", args.base_url)
    crawler = Crawler(args.base_url, max_pages=args.max_pages, concurrency=args.concurrency, timeout=args.http_timeout)
    crawled = await crawler.crawl()

    pages = {url: data for url, data in crawled.items() if data.get("status") == 200}
    logger.info("Crawl complete. %s pages with HTTP 200", len(pages))

    structure_detector = StructureDetector(args.base_url)
    classifier = PageClassifier()
    issue_detector = IssueDetector()
    scorer = Scorer()
    graph = GraphBuilder()

    page_summaries: List[Dict] = []

    async with BrowserAnalyzer(timeout=args.browser_timeout, headless=not args.headful) as analyzer:
        sem = asyncio.Semaphore(args.browser_concurrency)

        async def bounded_process(url_html):
            url, html = url_html
            async with sem:
                try:
                    return await process_page(
                        url,
                        html,
                        analyzer,
                        structure_detector,
                        classifier,
                        issue_detector,
                        scorer,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Processing failed for %s", url)
                    return {
                        "url": url,
                        "page_type": "unknown",
                        "issues": [
                            {
                                "page": url,
                                "category": "runtime",
                                "title": "Page processing failed",
                                "severity": "critical",
                                "details": {"error": str(exc)},
                            }
                        ],
                        "score": 0,
                    }

        tasks = [bounded_process(item) for item in pages.items()]
        for coro in asyncio.as_completed(tasks):
            result = await coro
            page_summaries.append(result)
            graph.add_page(result["url"], result.get("page_type", "unknown"), result.get("score", 0))
            graph.add_issues(result["url"], result.get("issues", []))

    global_score = scorer.global_score(page_summaries)

    report = {
        "base_url": args.base_url,
        "total_pages": len(pages),
        "global_hygiene_score": global_score,
        "pages": page_summaries,
        "graph": graph.to_report(),
    }

    output_path = Path(args.output)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Report written to %s", output_path)

    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Autonomous Bug & Hygiene Discovery Engine")
    parser.add_argument("base_url", help="Base URL to crawl")
    parser.add_argument("-o", "--output", default="qa_report.json", help="Path to JSON report output")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum pages to crawl")
    parser.add_argument("--concurrency", type=int, default=10, help="Crawler concurrency")
    parser.add_argument("--browser-concurrency", type=int, default=3, help="Parallel browser pages")
    parser.add_argument("--http-timeout", type=int, default=10, help="HTTP timeout seconds")
    parser.add_argument("--browser-timeout", type=int, default=15, help="Browser navigation timeout seconds")
    parser.add_argument("--headful", action="store_true", help="Run browser in headed mode")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.getLogger().setLevel(args.log_level.upper())
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
