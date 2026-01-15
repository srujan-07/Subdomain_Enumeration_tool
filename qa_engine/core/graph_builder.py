"""Knowledge graph for page → element → issue relationships."""

from typing import Dict, List, Any


class GraphBuilder:
    """Stores issues in a navigable graph structure."""

    def __init__(self) -> None:
        self.graph: Dict[str, Dict[str, Any]] = {}

    def add_page(self, url: str, page_type: str, hygiene_score: float) -> None:
        if url not in self.graph:
            self.graph[url] = {
                "type": page_type,
                "score": hygiene_score,
                "issues": [],
            }

    def add_issues(self, url: str, issues: List[Dict]) -> None:
        if url not in self.graph:
            self.add_page(url, "unknown", 0)
        self.graph[url]["issues"].extend(issues)

    def to_report(self) -> Dict[str, Any]:
        pages = []
        for url, data in self.graph.items():
            pages.append({
                "url": url,
                "type": data.get("type"),
                "score": data.get("score"),
                "issues": data.get("issues", []),
            })
        return {"pages": pages}
