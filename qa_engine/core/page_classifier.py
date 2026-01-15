"""Page type classification using DOM heuristics."""

from typing import Dict
from bs4 import BeautifulSoup


class PageClassifier:
    """Classify page types using structural and form heuristics."""

    def classify(self, html: str, dom_metrics: Dict) -> str:
        soup = BeautifulSoup(html, "html.parser")

        inputs = dom_metrics.get("inputCount", 0)
        buttons = dom_metrics.get("buttonCount", 0)
        tables = len(soup.find_all("table"))
        forms = len(soup.find_all("form"))
        lists = len(soup.find_all("ul")) + len(soup.find_all("ol"))
        charts = len(soup.find_all("canvas")) + len(soup.find_all("svg"))
        steps = len(soup.select("[role='tablist'] .step, .wizard-step, .step"))
        password_inputs = len(soup.find_all("input", {"type": "password"}))

        if password_inputs >= 1 or (forms >= 1 and inputs >= 3 and buttons >= 1):
            return "login"
        if charts >= 1 or "dashboard" in soup.text.lower():
            return "dashboard"
        if tables >= 1 and lists >= 1 and inputs < 5:
            return "list"
        if forms >= 1 and inputs >= 2 and buttons >= 1:
            return "form"
        if steps >= 1 or len(soup.select(".wizard")) >= 1:
            return "wizard"
        if charts >= 1 and tables >= 1:
            return "report"
        return "unknown"
