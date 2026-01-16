"""
QA INSPECTION ENGINE - QUICK START GUIDE

INSTALLATION
=============

1. Install dependencies
   pip install -r requirements.txt

2. Install Playwright browsers
   playwright install chromium

3. Verify installation
   python -c "from qa_engine.core import QAOrchestrator; print('OK')"


RUNNING THE SYSTEM
===================

Option 1: Full Stack (API + Frontend)
───────────────────────────────────────

Terminal 1 - Backend API:
  cd c:\Users\sruja\OneDrive\Documents\GitHub\Subdomain_Enumeration_tool
  python api.py

  Output:
    WARNING in app.run: This is a development server.
    Running on http://0.0.0.0:8000

Terminal 2 - Frontend:
  cd frontend
  npm run dev

  Output:
    ➜  Local:   http://localhost:5173/
    ➜  Press q to quit

Then open http://localhost:5173/ in browser


Option 2: Backend Only (API Testing)
──────────────────────────────────────

python api.py

Test with curl:
  # Start scan
  curl -X POST http://localhost:8000/api/scan \
    -H "Content-Type: application/json" \
    -d '{"url":"https://example.com","mode":"full"}'

  # Check status
  curl http://localhost:8000/api/scan/scan_abc123

  # Get hygiene data
  curl http://localhost:8000/api/hygiene


Option 3: Standalone QA Engine
─────────────────────────────────

Create test_qa.py:
  ```python
  import asyncio
  from qa_engine.core import QAOrchestrator

  async def main():
      orchestrator = QAOrchestrator(
          base_url='https://example.com',
          max_pages=10,
          browser_concurrency=2
      )
      results = await orchestrator.run('test_scan_1')
      
      # Print results
      for page in results['pages']:
          print(f"{page['url']}: {page['score']}/100")
      
      print(f"\nAverage: {results['summary']['avg_score']}/100")

  asyncio.run(main())
  ```

  Run:
  python test_qa.py


COMMON TASKS
=============

Task 1: Run Full Scan (Enumeration + QA)
─────────────────────────────────────────

Request:
POST http://localhost:8000/api/scan
Content-Type: application/json

{
  "url": "https://example.com",
  "depth": 2,
  "mode": "full",
  "wayback": false,
  "bruteforce": false,
  "validate_ssl": true
}

Response:
{
  "status": "started",
  "scan_id": "scan_abc123",
  "url": "https://example.com",
  ...
}

Then poll:
GET http://localhost:8000/api/scan/scan_abc123


Task 2: Analyze Results Programmatically
──────────────────────────────────────────

```python
import asyncio
import requests
import json
from qa_engine.hygiene_transformer import (
    qa_results_to_hygiene_pages,
    qa_results_to_worst_pages,
    qa_results_to_summary
)

# Assume scan is complete and we have scan_id
scan_id = 'scan_abc123'

# Get results from API
response = requests.get(f'http://localhost:8000/api/scan/{scan_id}')
scan = response.json()

# Extract QA results
qa_results = scan['qa_results']

# Transform to frontend format
pages = qa_results_to_hygiene_pages(qa_results)
summary = qa_results_to_summary(qa_results)
worst = qa_results_to_worst_pages(qa_results, limit=5)

# Print results
print(f"Scanned: {len(pages)} pages")
print(f"Average Score: {summary['averageScore']:.1f}/100")
print(f"Critical Issues: {summary['criticalIssues']}")
print(f"\nWorst Pages:")
for page in worst:
    print(f"  {page['url']}: {page['score']}/100 ({page['criticalIssueCount']} critical)")
```


Task 3: Monitor Scan with WebSocket
────────────────────────────────────

JavaScript:
```javascript
const scanId = 'scan_abc123';
const ws = new WebSocket(`ws://localhost:8000/ws/scan/${scanId}`);

ws.onmessage = (event) => {
  const { type, timestamp, data } = JSON.parse(event.data);
  
  switch (type) {
    case 'scan_started':
      console.log('Scan started at', timestamp);
      break;
    case 'url_discovered':
      console.log('Found URL:', data.url);
      break;
    case 'page_analyzed':
      console.log(`Analyzed: ${data.url} (${data.score}/100)`);
      break;
    case 'scan_completed':
      console.log('Scan complete:', data);
      break;
  }
};

ws.onerror = () => console.error('WebSocket error');
ws.onclose = () => console.log('WebSocket closed');
```

Python:
```python
import asyncio
import websockets
import json

async def monitor_scan(scan_id):
    uri = f"ws://localhost:8000/ws/scan/{scan_id}"
    
    async with websockets.connect(uri) as ws:
        async for message in ws:
            event = json.loads(message)
            print(f"{event['type']}: {event['data']}")
            
            if event['type'] == 'scan_completed':
                break

asyncio.run(monitor_scan('scan_abc123'))
```


Task 4: Get Worst Pages
────────────────────────

GET http://localhost:8000/api/scan/scan_abc123

Extract from response:
```json
{
  "worst_pages": [
    {
      "url": "https://example.com/broken",
      "type": "unknown",
      "score": 15.0,
      "criticalIssueCount": 5,
      "totalIssueCount": 12,
      "issues": [
        {
          "category": "functional",
          "title": "JavaScript error",
          "severity": "critical"
        },
        ...
      ]
    },
    ...
  ]
}
```


Task 5: Review Events for a Scan
──────────────────────────────────

GET http://localhost:8000/api/scan/scan_abc123/events

Response:
```json
{
  "scan_id": "scan_abc123",
  "events": [
    {
      "type": "scan_started",
      "timestamp": "2026-01-16T12:30:45.123Z",
      "data": { "base_url": "https://example.com" }
    },
    {
      "type": "url_discovered",
      "timestamp": "2026-01-16T12:30:46.456Z",
      "data": { "url": "https://example.com/page1" }
    },
    ...
  ]
}
```

Useful for debugging and audit trails.


TROUBLESHOOTING
================

Issue: "No module named 'qa_engine'"
───────────────────────────────────
Solution: Ensure you're in the project root directory
  cd c:\Users\sruja\OneDrive\Documents\GitHub\Subdomain_Enumeration_tool
  python api.py


Issue: Playwright browser not found
──────────────────────────────────────
Solution: Install Playwright browsers
  playwright install chromium


Issue: "Port 8000 already in use"
──────────────────────────────────
Solution: Kill the process or change port in api.py
  # In api.py, change:
  app.run(debug=True, host='0.0.0.0', port=8001)


Issue: Frontend can't connect to API
────────────────────────────────────
Solution: Check CORS configuration
  # In api.py, CORS is enabled for all origins
  # Ensure API is running and accessible
  curl http://localhost:8000/api/health


Issue: Scan hangs or times out
────────────────────────────────
Solution:
  1. Check browser memory usage (each instance ~100MB)
  2. Reduce max_pages in QAOrchestrator
  3. Increase browser_timeout if pages are slow
  4. Check logs for specific page timeouts


PERFORMANCE TIPS
=================

1. Adjust concurrency based on system resources
   - crawler_concurrency: 10 (default)
   - validator_concurrency: 20 (default)
   - browser_concurrency: 5 (default) ← most memory-intensive
   
   For limited resources:
   orchestrator = QAOrchestrator(
       base_url='https://example.com',
       crawler_concurrency=5,
       validator_concurrency=10,
       browser_concurrency=2  # Reduce browsers
   )

2. Reduce page limit for faster scans
   orchestrator = QAOrchestrator(
       base_url='https://example.com',
       max_pages=20  # Instead of 100
   )

3. Use headless mode (default)
   orchestrator = QAOrchestrator(
       base_url='https://example.com',
       headless=True  # Much faster
   )

4. Run multiple scans sequentially, not parallel


DEVELOPMENT WORKFLOW
=====================

1. Make changes to qa_engine/core/ modules
2. Test with standalone script (see Option 3)
3. Verify API integration:
   python api.py
   # In another terminal:
   curl -X POST http://localhost:8000/api/scan ...
4. Check frontend displays results correctly
5. Review logs for errors/warnings


PRODUCTION CONSIDERATIONS
===========================

Before deploying to production, consider:

1. Database backend (instead of SCAN_STORE dict)
2. Task queue (Celery, RQ) for scaling
3. Persistent storage for results
4. Authentication/authorization
5. Rate limiting
6. Logging to file/external service
7. Error monitoring (Sentry, etc.)
8. Health checks with retry logic
9. Graceful shutdown handling
10. Configuration management (env vars)

Example production setup:
  - Frontend: nginx reverse proxy
  - API: gunicorn/uWSGI with multiple workers
  - QA Engine: Celery worker pool
  - Storage: PostgreSQL
  - Cache: Redis
  - Monitoring: Prometheus + Grafana


NEXT STEPS
===========

1. Test with your target website
2. Adjust issue detection rules as needed
3. Customize scoring weights for your use case
4. Integrate with your dashboard
5. Set up automated scanning on schedule
6. Collect metrics and refine heuristics
"""
