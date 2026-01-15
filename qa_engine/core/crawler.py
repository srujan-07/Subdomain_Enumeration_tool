"""Asynchronous crawler to collect internal URLs and HTML content."""

import asyncio
import logging
from typing import Dict, Set, List
from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Crawler:
    """Simple asynchronous crawler for internal links."""

    def __init__(
        self,
        base_url: str,
        max_pages: int = 100,
        concurrency: int = 10,
        timeout: int = 10,
    ) -> None:
        self.base_url = self._normalize_base(base_url)
        self.max_pages = max_pages
        self.concurrency = concurrency
        self.timeout = timeout
        self.visited: Set[str] = set()
        self.results: Dict[str, Dict] = {}

    @staticmethod
    def _normalize_base(url: str) -> str:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"https://{url}"
            parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _is_internal(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            base_netloc = urlparse(self.base_url).netloc
            return parsed.netloc == base_netloc or parsed.netloc.endswith(f".{base_netloc}")
        except Exception:
            return False

    async def _fetch(self, client: httpx.AsyncClient, url: str) -> None:
        if len(self.results) >= self.max_pages:
            return
        if url in self.visited:
            return
        self.visited.add(url)

        try:
            logger.debug("Fetching %s", url)
            response = await client.get(url, timeout=self.timeout, follow_redirects=True)
            status = response.status_code
            html = response.text if status == 200 else ""
            self.results[url] = {
                "status": status,
                "html": html,
                "content_type": response.headers.get("content-type", ""),
            }

            if status == 200 and "text/html" in response.headers.get("content-type", ""):
                for link in self._extract_links(url, html):
                    if len(self.results) >= self.max_pages:
                        break
                    if link not in self.visited:
                        await self.queue.put(link)
        except httpx.HTTPError as exc:
            logger.warning("Request failed %s: %s", url, exc)
        except Exception as exc:  # noqa: BLE001
            logger.error("Unexpected error fetching %s: %s", url, exc)

    def _extract_links(self, base_url: str, html: str) -> List[str]:
        links: List[str] = []
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["a", "link", "script", "form"]):
            href = tag.get("href") or tag.get("src") or tag.get("action")
            if not href:
                continue
            absolute = urljoin(base_url, href)
            if self._is_internal(absolute):
                links.append(absolute.split("#")[0])
        return links

    async def crawl(self) -> Dict[str, Dict]:
        """Crawl starting from base URL and return page map."""
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        await self.queue.put(self.base_url)

        async with httpx.AsyncClient(headers={"User-Agent": "QA-Auto-Engine/1.0"}) as client:
            workers = [asyncio.create_task(self._worker(client)) for _ in range(self.concurrency)]
            await self.queue.join()
            for worker in workers:
                worker.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
        return self.results

    async def _worker(self, client: httpx.AsyncClient) -> None:
        while True:
            url = await self.queue.get()
            try:
                await self._fetch(client, url)
            finally:
                self.queue.task_done()
