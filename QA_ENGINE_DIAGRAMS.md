"""
QA INSPECTION ENGINE - SYSTEM DIAGRAMS

ARCHITECTURE DIAGRAM
════════════════════

┌──────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React/TypeScript)                     │
│                         http://localhost:5173                             │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ HygieneDashboard                                                   │ │
│  │ ┌──────────────────────┐  ┌──────────────────────────────────────┐ │ │
│  │ │  Hygiene Charts      │  │  Worst Pages Table                   │ │ │
│  │ │  - Avg Score         │  │  - Ranked by score (worst first)     │ │ │
│  │ │  - Distribution      │  │  - Issue counts                      │ │ │
│  │ │  - Trends            │  │  - Quick access to details           │ │ │
│  │ └──────────────────────┘  └──────────────────────────────────────┘ │ │
│  │                                                                      │ │
│  │ LiveStats  |  ActivityFeed  |  PageList  |  KnowledgeGraph         │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                              ↕ (hygieneService)                          │
│                    Fetches from /api/hygiene (REST)                      │
│                  or WebSocket ws://localhost:8000/ws                     │
└──────────────────────────────────────────────────────────────────────────┘
                                   ↕
┌──────────────────────────────────────────────────────────────────────────┐
│                     API SERVER (Flask/Python)                            │
│                     http://localhost:8000                                 │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Routes:                                                            │ │
│  │  POST /api/scan             ← Start new scan                      │ │
│  │  GET /api/scan/<id>         ← Get status & results                │ │
│  │  GET /api/scan/<id>/events  ← Event history (polling)             │ │
│  │  GET /api/hygiene           ← Latest results                      │ │
│  │  ws://localhost:8000/ws/... ← Real-time events (WebSocket)        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                  ↕                                        │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ SCAN_STORE (In-Memory)                                             │ │
│  │  scan_a1b2c3d4:                                                    │ │
│  │    ├─ status: completed                                           │ │
│  │    ├─ enum_results: {...}                                         │ │
│  │    ├─ qa_results: {...}                                           │ │
│  │    └─ hygiene_pages: [{url, type, score, issues}, ...]           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                  ↑                                        │
│  Background Thread (per scan):                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ QA Orchestrator (asyncio)                                          │ │
│  │                                                                    │ │
│  │ Phase 1: URL Enumeration (core.main_enum)                         │ │
│  │  └─ Emits: URL_DISCOVERED                                         │ │
│  │                                                                    │ │
│  │ Phase 2: QA Analysis                                              │ │
│  │  ├─ HTTP Validator (async parallel)                               │ │
│  │  │  └─ Emits: URL_VALIDATED                                      │ │
│  │  │                                                                │ │
│  │  └─ Browser Testing Loop (semaphore-limited concurrency)          │ │
│  │     ├─ BrowserAnalyzer (Playwright)                               │ │
│  │     │  ├─ Load page                                               │ │
│  │     │  ├─ Capture DOM, console, network, perf                    │ │
│  │     │  └─ Extract accessibility tree                              │ │
│  │     │                                                             │ │
│  │     ├─ StructureDetector                                          │ │
│  │     │  └─ Find: header, footer, nav, broken links                │ │
│  │     │                                                             │ │
│  │     ├─ PageClassifier                                             │ │
│  │     │  └─ Classify: login, form, list, dashboard, etc.           │ │
│  │     │                                                             │ │
│  │     ├─ IssueDetector (rule-based)                                │ │
│  │     │  └─ Detect: functional, UI, perf, a11y, content issues    │ │
│  │     │                                                             │ │
│  │     ├─ Scorer                                                     │ │
│  │     │  └─ Calculate: 100 - sum(deductions) = 0-100 score        │ │
│  │     │                                                             │ │
│  │     ├─ GraphBuilder                                               │ │
│  │     │  └─ Store: page → issues → categories → severity           │ │
│  │     │                                                             │ │
│  │     └─ EventBus                                                   │ │
│  │        └─ Emits: PAGE_ANALYZED, ISSUES_DETECTED, etc.            │ │
│  │                                                                    │ │
│  │ Transform Results → HygieneTransformer                            │ │
│  │  └─ qa_results → hygiene_pages (frontend format)                  │ │
│  │                                                                    │ │
│  │ Emit: SCAN_COMPLETED                                              │ │
│  │ Store in SCAN_STORE[scan_id]                                      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘


SCAN FLOW DIAGRAM
═════════════════

User initiates scan:
  POST /api/scan {url: "example.com", mode: "full"}
           ↓
  Generate scan_id → Return to user
           ↓
  Spawn background thread
           ↓
  
  ┌─ URL Enumeration (Phase 1) ──────────────────────────────────────┐
  │                                                                   │
  │  LiveCrawler → find URLs                                        │
  │  JSParser → extract URLs from JS                                │
  │  Robots/Sitemap → read rules                                    │
  │  Result: 87 URLs discovered                                     │
  │                                                                   │
  └────────────────────────────────────────────────────────────────────┘
           ↓
  Emit: URL_DISCOVERED (×87)
           ↓
  
  ┌─ HTTP Validation ──────────────────────────────────────────────────┐
  │                                                                   │
  │  HEAD/GET requests (async, parallel)                            │
  │  Filter: only HTTP 200 → 64 valid URLs                          │
  │                                                                   │
  └────────────────────────────────────────────────────────────────────┘
           ↓
  Emit: URL_VALIDATED (×87)
           ↓
  
  ┌─ Browser Testing Loop (Phase 2) ──────────────────────────────────┐
  │                                                                   │
  │  For each valid URL (concurrency = 5):                          │
  │    │                                                             │
  │    ├─ Load in Playwright → DOM snapshot                         │
  │    ├─ Detect: header, footer, nav                              │
  │    ├─ Classify: page type                                       │
  │    ├─ Detect: issues (bugs, perf, a11y)                        │
  │    ├─ Score: 100 - deductions                                   │
  │    ├─ Build: page → issue → category → severity                │
  │    └─ Emit: PAGE_ANALYZED                                       │
  │                                                                   │
  │  64 pages processed (2-5 minutes)                               │
  │                                                                   │
  └────────────────────────────────────────────────────────────────────┘
           ↓
  Emit: SCAN_COMPLETED
           ↓
  Transform & Store Results
           ↓
  Frontend updates
  (via polling or WebSocket)


ISSUE SCORING EXAMPLE
═════════════════════

Page: https://example.com/checkout
HTML: <form><input type="cc"></form>

Detection:
  Rule 1: JS errors in console
    → Issue: "Uncaught TypeError"
    → Severity: critical (-20 points)
    
  Rule 2: No form validation
    → Issue: "Credit card form missing validation"
    → Severity: high (-10 points)
    
  Rule 3: Missing footer
    → Issue: "Footer element not detected"
    → Severity: low (-2 points)

Calculation:
  Base Score:        100
  Critical issue:    -20
  High issue:        -10
  Low issue:         -2
  ───────────────────────
  Final Score:        68

Display: 68/100 with 3 issues (1 critical, 1 high, 1 low)


WEBSOCKET EVENT FLOW
════════════════════

Frontend connects:
  ws://localhost:8000/ws/scan/scan_a1b2c3d4
           ↓
Server registers connection
           ↓
Backend broadcasts events as they occur:
           
  1. scan_started
     {"type": "scan_started", "timestamp": "...", "data": {"base_url": "..."}}
           ↓
  2. url_discovered (×87)
     {"type": "url_discovered", "timestamp": "...", "data": {"url": "..."}}
           ↓
  3. url_validated (×87)
     {"type": "url_validated", "timestamp": "...", "data": {"url": "...", "status": 200, "valid": true}}
           ↓
  4. page_testing_started (×64)
     {"type": "page_testing_started", "timestamp": "...", "data": {"url": "..."}}
           ↓
  5. page_analyzed (×64)
     {"type": "page_analyzed", "timestamp": "...", "data": {"url": "...", "page_type": "form", "score": 68}}
           ↓
  6. scan_completed
     {"type": "scan_completed", "timestamp": "...", "data": {"total_discovered": 87, "total_valid": 64, ...}}
           ↓
Frontend updates UI after each event:
  - url_discovered: increment counter
  - page_analyzed: update worst pages table, recalculate average
  - scan_completed: finalize charts, show summary


CONCURRENCY MODEL
═════════════════

URL Crawling:
  ├─ LiveCrawler (queue + workers): 10 concurrent
  └─ Result: 87 URLs discovered

HTTP Validation:
  ├─ URLValidator (async batch): 20 concurrent
  └─ Result: 64 valid (HTTP 200)

Browser Testing:
  ├─ BrowserAnalyzer (semaphore): 5 concurrent
  ├─ Each page: ~500ms-1s
  ├─ 64 pages ÷ 5 concurrent = ~13 serial rounds
  └─ Total: ~2-5 minutes

Memory Usage:
  ├─ Base: ~100MB
  ├─ Per browser: ~80-100MB
  ├─ 5 concurrent: ~500MB
  └─ Total: ~600MB


DATA TRANSFORMATION
═══════════════════

Raw QA Results:
{
  "pages": [
    {
      "url": "...",
      "page_type": "form",
      "score": 68,
      "issues": [
        {"category": "functional", "title": "...", "severity": "critical", ...},
        ...
      ],
      ...
    }
  ],
  "summary": {
    "total_discovered": 87,
    "total_valid": 64,
    "total_analyzed": 64,
    "avg_score": 71.5
  }
}
        ↓
HygieneTransformer.qa_results_to_hygiene_pages()
        ↓
Frontend Format:
[
  {
    "url": "...",
    "type": "form",
    "score": 68,
    "criticalIssueCount": 1,
    "totalIssueCount": 3,
    "issues": [
      {"category": "functional", "title": "...", "severity": "critical", ...},
      ...
    ]
  }
]
        ↓
HygieneDashboard renders:
  ├─ Charts (average score, distribution)
  ├─ Worst Pages Table (sorted by score)
  ├─ Stats Grid (total issues, critical count)
  └─ Live updates (if WebSocket connected)


ERROR HANDLING FLOW
═══════════════════

Issue during page analysis:
           ↓
Try-catch in orchestrator._analyze_single_page()
           ↓
Caught Exception:
  - Log error
  - Emit ISSUES_DETECTED event
  - Return error result
           ↓
Page still included in results (with error flag)
           ↓
Other pages continue processing
           ↓
SCAN_COMPLETED still emitted with partial results


Module Dependency Graph:
════════════════════════

orchestrator.py
  ├── crawler.py (async)
  ├── url_validator.py (async)
  ├── browser_analyzer.py (async)
  ├── structure_detector.py
  ├── page_classifier.py
  ├── issue_detector.py
  ├── scorer.py
  ├── graph_builder.py
  ├── events.py
  └── hygiene_transformer.py

api.py
  ├── core.main_enum (URLEnumerator)
  ├── orchestrator.py (QAOrchestrator)
  ├── events.py (event_bus)
  ├── hygiene_transformer.py
  └── streaming.py (WebSocket)

frontend/
  └── hygieneService.ts
      ├── /api/hygiene (REST)
      ├── /api/scan/<id> (REST)
      └── ws://localhost:8000/ws/scan/<id> (WebSocket)
"""
