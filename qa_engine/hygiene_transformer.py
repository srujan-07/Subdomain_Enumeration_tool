"""Transform QA analysis results into frontend-compatible hygiene payloads."""

from typing import Dict, List, Any


def qa_results_to_hygiene_pages(qa_results: Dict[str, Any]) -> List[Dict]:
    """
    Transform QA orchestrator results into hygiene page format.

    Input: {pages: [...], summary: {...}, graph: {...}}
    Output: [{url, type, score, issues, criticalIssueCount, totalIssueCount}, ...]
    """
    pages = []
    for page_data in qa_results.get("pages", []):
        page = {
            "url": page_data.get("url"),
            "type": page_data.get("page_type", "unknown"),
            "score": page_data.get("score", 0),
            "issues": _transform_issues(page_data.get("issues", [])),
            "criticalIssueCount": page_data.get("critical_issue_count", 0),
            "totalIssueCount": page_data.get("total_issue_count", 0),
        }
        pages.append(page)

    # Sort by score descending (worst first)
    pages.sort(key=lambda p: p["score"])

    return pages


def _transform_issues(issues: List[Dict]) -> List[Dict]:
    """Transform issue format from detector to frontend."""
    transformed = []
    for issue in issues:
        transformed.append({
            "category": issue.get("category", "unknown"),
            "title": issue.get("title", "Unknown issue"),
            "severity": issue.get("severity", "low"),
            "details": issue.get("details", {}),
        })
    return transformed


def qa_results_to_summary(qa_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract summary metrics from QA results."""
    summary = qa_results.get("summary", {})
    pages = qa_results.get("pages", [])

    total_issues = sum(p.get("total_issue_count", 0) for p in pages)
    critical_issues = sum(p.get("critical_issue_count", 0) for p in pages)

    return {
        "totalDiscovered": summary.get("total_discovered", 0),
        "totalValid": summary.get("total_valid", 0),
        "totalAnalyzed": summary.get("total_analyzed", 0),
        "averageScore": summary.get("avg_score", 0),
        "totalIssues": total_issues,
        "criticalIssues": critical_issues,
    }


def qa_results_to_worst_pages(
    qa_results: Dict[str, Any], limit: int = 10
) -> List[Dict]:
    """Extract worst performing pages sorted by score."""
    pages = qa_results_to_hygiene_pages(qa_results)
    # Already sorted by score (worst first)
    return pages[:limit]
