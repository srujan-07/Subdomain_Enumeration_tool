"""HTTP status validation for discovered URLs."""

import asyncio
import logging
from typing import Dict, Set, Tuple
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


class URLValidator:
    """Validate HTTP status codes for URLs before browser testing."""

    def __init__(self, timeout: int = 10, concurrency: int = 20) -> None:
        self.timeout = timeout
        self.concurrency = concurrency

    async def validate_batch(self, urls: list[str]) -> Dict[str, Dict]:
        """
        Validate HTTP status for a batch of URLs.

        Returns:
            {url: {status: int, valid: bool}}
        """
        results = {}
        sem = asyncio.Semaphore(self.concurrency)

        async def check_url(url: str) -> Tuple[str, Dict]:
            async with sem:
                return url, await self._check_single(url)

        tasks = [check_url(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for url, result in responses:
            if isinstance(result, Exception):
                results[url] = {"status": 0, "valid": False, "error": str(result)}
            else:
                results[url] = result

        return results

    async def _check_single(self, url: str) -> Dict:
        """Check single URL status."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.head(
                    url,
                    follow_redirects=True,
                    headers={"User-Agent": "QA-Auto-Engine/1.0"},
                )
                status = response.status_code
                return {
                    "status": status,
                    "valid": status == 200,
                    "content_type": response.headers.get("content-type", ""),
                }
        except httpx.TimeoutException:
            logger.warning(f"Timeout validating {url}")
            return {"status": 0, "valid": False, "error": "timeout"}
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error validating {url}: {e}")
            return {"status": 0, "valid": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error validating {url}: {e}")
            return {"status": 0, "valid": False, "error": str(e)}

    def filter_valid_urls(self, validation_results: Dict[str, Dict]) -> Set[str]:
        """Extract only HTTP 200 URLs from validation results."""
        return {url for url, result in validation_results.items() if result.get("valid")}
