"""
QA INSPECTION ENGINE - API REFERENCE

REST ENDPOINTS
==============

1. Health Check
───────────────────────────────────────────────────────────
GET /api/health

Response (200):
{
  "status": "ok",
  "service": "url-enumeration-api"
}


2. Start Scan
───────────────────────────────────────────────────────────
POST /api/scan

Request Body:
{
  "url": "https://example.com",           // Required: Target domain
  "depth": 2,                             // Optional: Crawl depth (default: 2)
  "mode": "full|crawl|qa",                // Optional: Mode (default: "full")
                                          // - full: URL enum + QA analysis
                                          // - crawl: URL enum only
                                          // - qa: QA analysis only (uses cached URLs)
  "wayback": true,                        // Optional: Use Wayback Machine (default: false)
  "bruteforce": true,                     // Optional: Brute force (default: false)
  "validate_ssl": true                    // Optional: Filter to HTTP 200 (default: true)
}

Response (202 Accepted):
{
  "status": "started",
  "scan_id": "scan_a1b2c3d4",
  "url": "https://example.com",
  "config": {...},
  "message": "Scan started successfully"
}

Errors:
- 400: Missing 'url' field
- 500: Server error


3. Get Scan Status & Results
───────────────────────────────────────────────────────────
GET /api/scan/<scan_id>

Response (200 - Running):
{
  "scan_id": "scan_a1b2c3d4",
  "status": "running",
  "url": "https://example.com",
  "config": {...},
  "progress": 10
}

Response (200 - Completed):
{
  "scan_id": "scan_a1b2c3d4",
  "status": "completed",
  "url": "https://example.com",
  "config": {...},
  "progress": 100,
  "hygiene_pages": [
    {
      "url": "https://example.com/page1",
      "type": "form",
      "score": 85.0,
      "criticalIssueCount": 1,
      "totalIssueCount": 5,
      "issues": [
        {
          "category": "functional",
          "title": "JavaScript error",
          "severity": "high",
          "details": {...}
        },
        ...
      ]
    },
    ...
  ],
  "summary": {
    "totalDiscovered": 87,
    "totalValid": 64,
    "totalAnalyzed": 64,
    "averageScore": 72.3,
    "totalIssues": 156,
    "criticalIssues": 12
  },
  "worst_pages": [...],                   // Top 5 worst performing pages
  "enum_results": {...}                   // URL enumeration results (if available)
}

Response (200 - Failed):
{
  "scan_id": "scan_a1b2c3d4",
  "status": "failed",
  "url": "https://example.com",
  "config": {...},
  "error": "Error message"
}

Errors:
- 404: Scan not found
- 500: Server error


4. Cancel Scan
───────────────────────────────────────────────────────────
DELETE /api/scan/<scan_id>

Response (200):
{
  "scan_id": "scan_a1b2c3d4",
  "status": "cancelled",
  "message": "Scan cancelled successfully"
}

Note: Currently returns success but doesn't actually cancel.
      (TODO: Implement cancel token support)


5. Get Latest Hygiene Data
───────────────────────────────────────────────────────────
GET /api/hygiene

Response (200):
[
  {
    "url": "https://example.com/page1",
    "type": "form",
    "score": 85.0,
    "criticalIssueCount": 1,
    "totalIssueCount": 5,
    "issues": [...]
  },
  ...
]

Returns hygiene data from latest completed scan.
Returns [] if no scan has completed.


6. Get Scan Event History
───────────────────────────────────────────────────────────
GET /api/scan/<scan_id>/events

Response (200):
{
  "scan_id": "scan_a1b2c3d4",
  "events": [
    {
      "type": "scan_started",
      "timestamp": "2026-01-16T12:30:45.123Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "base_url": "https://example.com"
      }
    },
    {
      "type": "url_discovered",
      "timestamp": "2026-01-16T12:30:46.456Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "url": "https://example.com/page1"
      }
    },
    {
      "type": "url_validated",
      "timestamp": "2026-01-16T12:30:47.789Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "url": "https://example.com/page1",
        "status": 200,
        "valid": true
      }
    },
    {
      "type": "page_testing_started",
      "timestamp": "2026-01-16T12:30:48.012Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "url": "https://example.com/page1"
      }
    },
    {
      "type": "page_analyzed",
      "timestamp": "2026-01-16T12:30:55.345Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "url": "https://example.com/page1",
        "page_type": "form",
        "score": 85.0
      }
    },
    {
      "type": "scan_completed",
      "timestamp": "2026-01-16T12:31:00.678Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "total_discovered": 87,
        "total_valid": 64,
        "total_analyzed": 64,
        "avg_score": 72.3
      }
    }
  ]
}

Use this for REST-based polling. Real-time updates prefer WebSocket.


WEBSOCKET ENDPOINT
==================

7. Real-time Event Stream
───────────────────────────────────────────────────────────
ws://localhost:8000/ws/scan/<scan_id>

Connect to receive real-time QAEvent stream during scan.

Message (from server):
{
  "type": "page_analyzed",
  "timestamp": "2026-01-16T12:30:55.345Z",
  "scan_id": "scan_a1b2c3d4",
  "data": {
    "url": "https://example.com/page1",
    "page_type": "form",
    "score": 85.0
  }
}

Connection Management:
- Connect before or during scan
- Automatically receives all subsequent events
- Closed manually or on error
- Reconnect logic handled by frontend

Usage (JavaScript):
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/scan/scan_a1b2c3d4');

ws.onmessage = (event) => {
  const qaEvent = JSON.parse(event.data);
  console.log(qaEvent.type, qaEvent.data);
  // Update UI based on event
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket closed');
};
```


EVENT TYPES
===========

EventType Values:
- scan_started: Scan initiated
- url_discovered: URL found during crawling
- url_validated: URL HTTP status checked
- page_testing_started: Browser test starting
- page_analyzed: Page analysis complete
- issues_detected: Issues found for page
- score_updated: Hygiene score calculated
- scan_completed: All analysis complete
- scan_failed: Scan encountered error


ISSUE CATEGORIES & SEVERITIES
==============================

Issue Categories:
- functional: Code errors, broken interactions
- ui: Visual/structural problems
- performance: Load time, resource issues
- accessibility: ARIA, labels, navigation
- content: Placeholder text, hygiene issues

Severity Levels (and scoring impact):
- critical: -20 points (e.g., unhandled exceptions)
- high: -10 points (e.g., network failures, missing nav)
- medium: -5 points (e.g., slow loads, heavy DOM)
- low: -2 points (e.g., missing footer, placeholder text)


PAGE TYPES
==========

Classification Results:
- login: Login/authentication page
- form: Data entry form
- list: List of items (table, grid)
- dashboard: Analytics/overview page
- report: Report page (charts, tables)
- wizard: Multi-step workflow
- unknown: Unclassified


EXAMPLE WORKFLOWS
=================

Workflow 1: Full Scan
────────────────────
1. POST /api/scan
   → scan_id = "scan_abc123"

2. Either:
   A. Poll: GET /api/scan/scan_abc123 (every 5 seconds)
   B. WebSocket: ws://localhost:8000/ws/scan/scan_abc123

3. When status == "completed"
   → Display hygiene_pages[], summary

Workflow 2: Re-use Enumeration
──────────────────────────────
1. POST /api/scan (mode: "crawl")
   → Complete URL enumeration

2. POST /api/scan (mode: "qa")
   → Run QA on previously discovered URLs

Workflow 3: Stream Events to Dashboard
──────────────────────────────────────
1. Open WebSocket
2. For each event:
   - url_discovered: Update URL count
   - page_analyzed: Update worst pages table
   - score_updated: Re-sort by score
   - scan_completed: Finalize charts

Workflow 4: Integration with CI/CD
───────────────────────────────────
```bash
# Start scan
SCAN=$(curl -X POST http://api:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","mode":"full"}')

SCAN_ID=$(echo $SCAN | jq -r '.scan_id')

# Poll until complete
while true; do
  STATUS=$(curl http://api:8000/api/scan/$SCAN_ID)
  STATE=$(echo $STATUS | jq -r '.status')
  
  if [ "$STATE" == "completed" ]; then
    SCORE=$(echo $STATUS | jq -r '.summary.averageScore')
    CRITICAL=$(echo $STATUS | jq -r '.summary.criticalIssues')
    
    echo "Scan complete: Score=$SCORE, Critical=$CRITICAL"
    
    if [ "$CRITICAL" -gt 0 ]; then
      exit 1  # Fail if critical issues found
    fi
    exit 0
  fi
  
  sleep 5
done
```


HEADERS & AUTHENTICATION
========================

CORS:
- Origin: * (configured for development)
- Methods: GET, POST, DELETE
- Headers: Content-Type, Accept

Authentication:
- None (currently open)
- TODO: Add bearer token support


RATE LIMITING
=============

Not yet implemented. Recommended additions:
- 1 scan per 10 seconds per client
- 10 scans max concurrent
- Store results for 1 hour per scan

"""
