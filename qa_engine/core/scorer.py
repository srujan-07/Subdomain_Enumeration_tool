"""Hygiene score calculation."""

from typing import List, Dict

WEIGHTS = {
    "critical": 20,
    "high": 10,
    "medium": 5,
    "low": 2,
}


class Scorer:
    """Compute hygiene scores per page and globally."""

    def __init__(self, base_score: int = 100) -> None:
        self.base_score = base_score

    def score_page(self, issues: List[Dict]) -> float:
        score = float(self.base_score)
        for issue in issues:
            sev = issue.get("severity", "low")
            score -= WEIGHTS.get(sev, 1)
        return max(score, 0.0)

    def global_score(self, pages: List[Dict]) -> float:
        if not pages:
            return 0.0
        return sum(p.get("score", 0) for p in pages) / len(pages)
