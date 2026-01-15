"""Detect functional, UI, performance, accessibility, and content hygiene issues."""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

SEVERITIES = {
    "critical": 5,
    "high": 3,
    "medium": 2,
    "low": 1,
}


class IssueDetector:
    """Rule-based detector using collected signals."""

    def detect(self, page_data: Dict) -> List[Dict]:
        issues: List[Dict] = []

        url = page_data.get("url")
        console_logs = page_data.get("console_logs", [])
        network_failures = page_data.get("network_failures", [])
        dom_metrics = page_data.get("dom_metrics", {})
        structure = page_data.get("structure", {})
        perf = page_data.get("performance", {})
        accessibility_tree = page_data.get("accessibility_tree")

        # Functional: JS errors
        for log in console_logs:
            if log.get("type") in {"error", "assert"}:
                issues.append(self._issue(url, "functional", "JavaScript error", "high", details=log))

        # Functional: failed requests
        for failure in network_failures:
            issues.append(
                self._issue(url, "functional", "Network request failed", "high", details=failure)
            )

        # UI: missing header/footer/nav
        if not structure.get("has_header"):
            issues.append(self._issue(url, "ui", "Missing header", "low"))
        if not structure.get("has_footer"):
            issues.append(self._issue(url, "ui", "Missing footer", "low"))
        if not structure.get("has_nav"):
            issues.append(self._issue(url, "ui", "Missing navigation", "medium"))

        # UI: broken links/images
        for bl in structure.get("broken_links", []):
            sev = "medium" if bl.get("type") == "link" else "low"
            issues.append(self._issue(url, "ui", f"Broken {bl.get('type')}", sev, details=bl))

        # Performance: slow load
        nav = (perf or {}).get("navigation") or {}
        duration = nav.get("duration")
        if duration and duration > 4000:
            issues.append(self._issue(url, "performance", "Slow navigation (>4s)", "medium", details={"duration": duration}))

        # Performance: heavy resources (approx by node count)
        if dom_metrics.get("nodeCount", 0) > 4000:
            issues.append(self._issue(url, "performance", "Heavy DOM (>4000 nodes)", "medium"))

        # Accessibility: simple checks from accessibility tree
        if accessibility_tree:
            missing_names = self._count_missing_accessible_names(accessibility_tree)
            if missing_names > 0:
                issues.append(
                    self._issue(url, "accessibility", f"Elements missing accessible names ({missing_names})", "medium")
                )

        # Content hygiene
        dom_snapshot = page_data.get("dom_snapshot", "")
        if "lorem ipsum" in dom_snapshot.lower():
            issues.append(self._issue(url, "content", "Placeholder text present", "low"))

        if dom_metrics.get("imgCount", 0) > 0 and dom_snapshot.lower().count("alt=\"\"") > 0:
            issues.append(self._issue(url, "accessibility", "Images missing alt text", "low"))

        return issues

    def _issue(self, page: str, category: str, title: str, severity: str, details=None) -> Dict:
        return {
            "page": page,
            "category": category,
            "title": title,
            "severity": severity,
            "severity_weight": SEVERITIES.get(severity, 1),
            "details": details or {},
        }

    def _count_missing_accessible_names(self, tree) -> int:
        count = 0
        nodes = [tree]
        while nodes:
            node = nodes.pop()
            name = node.get("name") if isinstance(node, dict) else None
            role = node.get("role") if isinstance(node, dict) else None
            children = node.get("children", []) if isinstance(node, dict) else []
            if role in {"button", "link", "textbox", "combobox"} and not name:
                count += 1
            nodes.extend(children)
        return count
