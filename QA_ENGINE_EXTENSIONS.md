"""
QA INSPECTION ENGINE - EXTENSION & CUSTOMIZATION GUIDE

ADDING CUSTOM ISSUE DETECTORS
==============================

The IssueDetector class is designed to be extended with custom rules.
Each rule is a simple heuristic that detects a specific type of problem.

Example 1: Add detector for custom JavaScript framework errors
───────────────────────────────────────────────────────────────

In qa_engine/core/issue_detector.py, add to the detect() method:

    # Custom: React/Vue framework errors
    for log in console_logs:
        if "React" in log.get("text", "") or "Vue" in log.get("text", ""):
            if log.get("type") in {"error", "warning"}:
                issues.append(self._issue(
                    url, 
                    "functional",
                    f"Framework error: {log.get('text', '')[:50]}",
                    "high",
                    details=log
                ))

Then create a scan:
  POST /api/scan
  {"url": "https://example.com", "mode": "full"}

The detector will automatically catch framework errors.


Example 2: Add detector for missing payment form validation
────────────────────────────────────────────────────────────

In qa_engine/core/issue_detector.py:

    # Custom: Payment pages should have strong validation
    if page_data.get("page_type") == "form":
        html = page_data.get("raw_html", "")
        has_card_input = "type=\"cc" in html or "card" in html.lower()
        has_validation = "validate" in html.lower() or "required" in html.lower()
        
        if has_card_input and not has_validation:
            issues.append(self._issue(
                url,
                "functional",
                "Payment form missing validation",
                "critical"
            ))


Example 3: Add detector for responsive design issues
──────────────────────────────────────────────────────

In qa_engine/core/issue_detector.py:

    # Custom: Check viewport meta tag
    html = page_data.get("raw_html", "")
    if "<meta name=\"viewport\"" not in html:
        issues.append(self._issue(
            url,
            "ui",
            "Missing viewport meta tag",
            "medium"
        ))


ADDING CUSTOM PAGE CLASSIFIERS
===============================

Extend PageClassifier to recognize custom page types.

Example: Detect e-commerce product pages
──────────────────────────────────────────

In qa_engine/core/page_classifier.py, modify the classify() method:

    def classify(self, html: str, dom_metrics: Dict) -> str:
        soup = BeautifulSoup(html, "html.parser")
        
        # ... existing checks ...
        
        # Custom: Product pages
        price_tags = soup.find_all("span", {"class": ["price", "product-price"]})
        add_to_cart = soup.find_all("button", {"class": ["add-to-cart", "add-cart"]})
        
        if len(price_tags) >= 1 and len(add_to_cart) >= 1:
            return "product"
        
        return "unknown"

Now pages will be classified as "product" and appear in dashboard.


CUSTOMIZING SCORING WEIGHTS
=============================

Adjust how much each issue type impacts the overall score.

In qa_engine/core/scorer.py, modify WEIGHTS:

    WEIGHTS = {
        "critical": 30,  # Increased from 20 (more severe)
        "high": 15,      # Increased from 10
        "medium": 5,     # Unchanged
        "low": 1,        # Decreased from 2 (less impact)
    }

Now a critical issue costs 30 points instead of 20.

For different domains, create variants:
    
    class EcommerceSc​orer(Scorer):
        def __init__(self):
            super().__init__(base_score=100)
            self.weights = {
                "critical": 25,  # Payment/security critical
                "high": 15,
                "medium": 5,
                "low": 1,
            }
    
    score = self.weights.get(severity, 1)


CREATING CUSTOM STRUCTURE DETECTORS
====================================

Extend StructureDetector to identify custom layout elements.

Example: Detect cookie consent banner
──────────────────────────────────────

In qa_engine/core/structure_detector.py:

    def analyze(self, url: str, html: str) -> Dict:
        # ... existing analysis ...
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Custom: Look for cookie banner
        cookie_banner = soup.find(
            attrs={"id": ["cookie", "cookie-consent", "gdpr-banner"]}
        )
        has_cookie_banner = cookie_banner is not None
        
        return {
            "has_header": ...,
            "has_footer": ...,
            "has_nav": ...,
            "has_cookie_banner": has_cookie_banner,  # Custom
            ...
        }

Then in issue_detector.py:

    if page_data.get("structure", {}).get("has_cookie_banner") is False:
        issues.append(self._issue(
            url,
            "compliance",
            "Missing cookie consent banner",
            "high"
        ))


INTEGRATING LLM ANALYSIS (FUTURE)
==================================

The architecture supports adding LLM-powered analysis without rewriting.

Example: Add GPT-based issue categorization
───────────────────────────────────────────

Create qa_engine/core/llm_analyzer.py:

    import openai
    
    class LLMAnalyzer:
        def __init__(self, api_key: str):
            openai.api_key = api_key
        
        async def classify_issue_severity(self, issue: Dict) -> str:
            """Use LLM to refine issue severity classification."""
            prompt = f"""
            Given this detected issue:
            {issue['title']}: {issue['details']}
            
            Is this critical, high, medium, or low severity?
            Respond with one word only.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.choices[0].message.content.lower()

Then in orchestrator.py:

    llm = LLMAnalyzer(api_key=os.getenv("OPENAI_API_KEY"))
    
    for issue in issues:
        # Optionally refine severity with LLM
        # refined_severity = await llm.classify_issue_severity(issue)
        # issue['severity'] = refined_severity
        pass


EXTENDING EVENT SYSTEM
======================

Add custom event types for domain-specific tracking.

Example: Add event for security issues
───────────────────────────────────────

In qa_engine/core/events.py, extend EventType:

    class EventType(Enum):
        # ... existing ...
        SECURITY_ISSUE_DETECTED = "security_issue_detected"
        PERFORMANCE_WARNING = "performance_warning"

Then emit custom events in orchestrator.py:

    if any(i.get("category") == "security" for i in issues):
        await event_bus.emit(
            create_event(
                EventType.SECURITY_ISSUE_DETECTED,
                scan_id,
                {
                    "url": url,
                    "count": len([i for i in issues if i.get("category") == "security"])
                }
            )
        )

Frontend subscribes to receive alerts.


CUSTOM RESULT TRANSFORMATIONS
==============================

Transform raw QA results to different formats.

Example: Create Slack report transformer
──────────────────────────────────────────

Create qa_engine/exporters.py:

    def qa_results_to_slack_message(qa_results: Dict) -> str:
        pages = qa_results['pages']
        summary = qa_results['summary']
        
        worst = sorted(pages, key=lambda p: p['score'])[:3]
        
        message = f"""
        *QA Scan Report*
        Scanned: {summary['total_analyzed']} pages
        Avg Score: {summary['avg_score']:.1f}/100
        Critical Issues: {summary['critical_issues']}
        
        *Worst Pages:*
        """
        
        for page in worst:
            message += f"\n• {page['url']}: {page['score']:.0f}/100"
        
        return message

Usage:
    from qa_engine.exporters import qa_results_to_slack_message
    message = qa_results_to_slack_message(qa_results)
    # Send to Slack webhook...


PERFORMANCE OPTIMIZATION
=========================

Optimize for your specific use case.

1. Reduce Browser Concurrency for Large Pages
────────────────────────────────────────────

    orchestrator = QAOrchestrator(
        base_url='https://example.com',
        browser_concurrency=2,  # Instead of 5
        max_pages=50            # Reduce scope
    )

2. Add Caching for Repeated Scans
──────────────────────────────────

    class CachedCrawler:
        def __init__(self, base_crawler):
            self.crawler = base_crawler
            self.cache = {}
        
        async def crawl(self):
            cache_key = self.crawler.base_url
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            result = await self.crawler.crawl()
            self.cache[cache_key] = result
            return result

3. Parallelize Independent Analysis
───────────────────────────────────

    # StructureDetector and PageClassifier don't depend on browser
    # Run them in parallel with browser testing
    
    await asyncio.gather(
        analyzer.analyze(url),
        asyncio.to_thread(classifier.classify, html, dom_metrics),
        asyncio.to_thread(structure_detector.analyze, url, html)
    )

4. Stream Results Instead of Waiting
──────────────────────────────────────

    # Emit PAGE_ANALYZED immediately after each page
    # Frontend updates incrementally instead of waiting for full scan
    
    for url in urls:
        result = await analyze_page(url)
        yield result  # Stream to frontend via SSE or WebSocket
        await event_bus.emit(create_event(..., result))


TESTING CUSTOM EXTENSIONS
==========================

Example test for custom issue detector:

    import pytest
    from qa_engine.core.issue_detector import IssueDetector
    
    def test_custom_payment_validation_detector():
        detector = IssueDetector()
        
        page_data = {
            "url": "https://example.com/checkout",
            "page_type": "form",
            "raw_html": '<form><input type="cc"></form>',
            "console_logs": [],
            "network_failures": [],
        }
        
        issues = detector.detect(page_data)
        
        # Should detect missing validation
        assert any(i['title'] == "Payment form missing validation" for i in issues)
    
    pytest.main([__file__, "-v"])


CONFIGURATION MANAGEMENT
=========================

Create qa_engine/config.py for environment-specific settings:

    import os
    from dataclasses import dataclass
    
    @dataclass
    class QAConfig:
        max_pages: int = int(os.getenv("QA_MAX_PAGES", 100))
        browser_timeout: int = int(os.getenv("QA_BROWSER_TIMEOUT", 15))
        browser_concurrency: int = int(os.getenv("QA_BROWSER_CONCURRENCY", 5))
        headless: bool = os.getenv("QA_HEADLESS", "true").lower() == "true"
        
        @staticmethod
        def for_environment(env: str) -> "QAConfig":
            if env == "production":
                return QAConfig(max_pages=200, browser_concurrency=3)
            elif env == "staging":
                return QAConfig(max_pages=100, browser_concurrency=5)
            else:
                return QAConfig(max_pages=20, browser_concurrency=2)

Usage in api.py:

    from qa_engine.config import QAConfig
    
    config = QAConfig.for_environment(os.getenv("ENVIRONMENT", "dev"))
    orchestrator = QAOrchestrator(
        base_url=url,
        max_pages=config.max_pages,
        browser_concurrency=config.browser_concurrency,
        headless=config.headless
    )
"""
