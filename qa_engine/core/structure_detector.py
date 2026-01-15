"""Structural analysis for common layout elements and broken links."""

import logging
from collections import Counter
from typing import Dict, List, Set
from urllib.parse import urljoin

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class StructureDetector:
    """Detect layout structure and potential hygiene issues."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def analyze(self, url: str, html: str) -> Dict:
        soup = BeautifulSoup(html, "html.parser")

        header = soup.find("header") is not None
        footer = soup.find("footer") is not None
        nav = soup.find("nav") is not None

        class_counter = Counter()
        for el in soup.find_all(True):
            cls = el.get("class")
            if cls:
                class_counter.update(cls)

        repeated_classes = [c for c, count in class_counter.items() if count >= 5]

        broken_links = self._find_broken_links(url, soup)

        return {
            "has_header": header,
            "has_footer": footer,
            "has_nav": nav,
            "repeated_classes": repeated_classes,
            "broken_links": broken_links,
        }

    def _find_broken_links(self, url: str, soup: BeautifulSoup) -> List[Dict]:
        broken: List[Dict] = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                broken.append({"type": "image", "reason": "missing src", "element": str(img)[:120]})
                continue
            if src.startswith("data:"):
                continue
            full = urljoin(url, src)
            if full.lower().endswith((".svg", ".png", ".jpg", ".jpeg", ".gif")):
                # Cannot fetch here; mark as unchecked placeholder for later network failure matching.
                if "placeholder" in src.lower():
                    broken.append({"type": "image", "reason": "placeholder src", "src": full})
        for anchor in soup.find_all("a"):
            href = anchor.get("href")
            if href in ("#", "javascript:void(0)"):
                broken.append({"type": "link", "reason": "empty href", "element": str(anchor)[:120]})
        return broken
