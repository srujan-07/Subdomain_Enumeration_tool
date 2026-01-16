"""Playwright-based page analyzer to capture runtime signals."""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any

from playwright.async_api import async_playwright, Page, Browser, Playwright

logger = logging.getLogger(__name__)


class BrowserAnalyzer:
    """Encapsulates Playwright to analyze pages with runtime signals."""

    def __init__(self, timeout: int = 15, headless: bool = True) -> None:
        self.timeout = timeout
        self.headless = headless
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None

    async def __aenter__(self) -> "BrowserAnalyzer":
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def analyze(self, url: str) -> Dict[str, Any]:
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")

        page: Page = await self.browser.new_page()
        console_logs: List[Dict[str, Any]] = []
        network_failures: List[Dict[str, Any]] = []

        # Event hooks
        page.on(
            "console",
            lambda msg: console_logs.append(
                {
                    "type": msg.type,
                    "text": msg.text,
                    "location": msg.location,
                }
            ),
        )
        page.on(
            "requestfailed",
            lambda req: network_failures.append(
                {
                    "url": req.url,
                    "method": req.method,
                    "failure": req.failure,
                    "resource_type": req.resource_type,
                }
            ),
        )

        start = time.perf_counter()
        nav_status = "ok"
        try:
            await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
        except Exception as exc:  # noqa: BLE001
            nav_status = f"navigation_error: {exc}"
            logger.warning("Navigation failed for %s: %s", url, exc)

        # DOM snapshot
        dom_snapshot = await page.content()

        # Performance metrics (navigation entry)
        perf_entry = await page.evaluate(
            """
            () => {
                const nav = performance.getEntriesByType('navigation')[0] || {};
                const paint = performance.getEntriesByType('paint');
                return {
                    navigation: nav,
                    paint,
                    timing: performance.timing || {},
                };
            }
            """
        )

        # Basic page metrics
        dom_metrics = await page.evaluate(
            """
            () => ({
                nodeCount: document.getElementsByTagName('*').length,
                inputCount: document.querySelectorAll('input,select,textarea').length,
                buttonCount: document.querySelectorAll('button,[role="button"],input[type="submit"]').length,
                imgCount: document.querySelectorAll('img').length,
                linkCount: document.querySelectorAll('a').length,
            })
            """
        )

        # Accessibility tree
        accessibility_tree = await page.accessibility.snapshot()

        elapsed = time.perf_counter() - start

        await page.close()

        return {
            "url": url,
            "navigation_status": nav_status,
            "console_logs": console_logs,
            "network_failures": network_failures,
            "dom_snapshot": dom_snapshot,
            "dom_metrics": dom_metrics,
            "performance": perf_entry,
            "accessibility_tree": accessibility_tree,
            "elapsed": elapsed,
        }
