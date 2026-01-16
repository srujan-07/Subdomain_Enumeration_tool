"""
QA ENGINE - USAGE EXAMPLES

These examples demonstrate how to use the QA inspection system.

═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 1: Start a Full QA Scan (cURL)
═══════════════════════════════════════════════════════════════════════════════

Request:
--------
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org",
    "depth": 2,
    "mode": "full",
    "validate_ssl": true
  }'

Response (202 Accepted):
------------------------
{
  "status": "started",
  "scan_id": "scan_a1b2c3d4",
  "url": "https://httpbin.org",
  "config": {
    "depth": 2,
    "mode": "full",
    "wayback": false,
    "bruteforce": false,
    "validate_ssl": true
  },
  "message": "Scan started successfully"
}


═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 2: Poll Scan Status and Results
═══════════════════════════════════════════════════════════════════════════════

While running (progress):
------------------------
curl http://localhost:8000/api/scan/scan_a1b2c3d4

{
  "scan_id": "scan_a1b2c3d4",
  "status": "running",
  "url": "https://httpbin.org",
  "progress": 45,
  "config": {...}
}


After completion:
-----------------
curl http://localhost:8000/api/scan/scan_a1b2c3d4

{
  "scan_id": "scan_a1b2c3d4",
  "status": "completed",
  "url": "https://httpbin.org",
  "progress": 100,
  "hygiene_pages": [
    {
      "url": "https://httpbin.org/",
      "type": "unknown",
      "score": 92.0,
      "criticalIssueCount": 0,
      "totalIssueCount": 2,
      "issues": [
        {
          "category": "performance",
          "title": "Heavy DOM (>4000 nodes)",
          "severity": "medium",
          "details": {}
        },
        {
          "category": "ui",
          "title": "Missing footer",
          "severity": "low",
          "details": {}
        }
      ]
    },
    {
      "url": "https://httpbin.org/html",
      "type": "unknown",
      "score": 95.0,
      "criticalIssueCount": 0,
      "totalIssueCount": 1,
      "issues": [
        {
          "category": "ui",
          "title": "Missing navigation",
          "severity": "medium",
          "details": {}
        }
      ]
    }
  ],
  "summary": {
    "totalDiscovered": 23,
    "totalValid": 18,
    "totalAnalyzed": 18,
    "averageScore": 91.5,
    "totalIssues": 24,
    "criticalIssues": 0
  },
  "worst_pages": [
    {
      "url": "https://httpbin.org/status/500",
      "type": "unknown",
      "score": 75.0,
      "criticalIssueCount": 1,
      "totalIssueCount": 5,
      "issues": [...]
    },
    ...
  ]
}


═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 3: Get Latest Hygiene Data
═══════════════════════════════════════════════════════════════════════════════

Request:
--------
curl http://localhost:8000/api/hygiene

Response (200):
---------------
[
  {
    "url": "https://httpbin.org/",
    "type": "unknown",
    "score": 92.0,
    "criticalIssueCount": 0,
    "totalIssueCount": 2,
    "issues": [...]
  },
  ...
]


═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 4: WebSocket Real-time Updates (JavaScript)
═══════════════════════════════════════════════════════════════════════════════

const scanId = 'scan_a1b2c3d4';
const ws = new WebSocket(`ws://localhost:8000/ws/scan/${scanId}`);

let pagesAnalyzed = 0;
let avgScore = 0;

ws.onmessage = (event) => {
  const qaEvent = JSON.parse(event.data);
  
  console.log(`[${qaEvent.type}] ${qaEvent.timestamp}`);
  
  switch (qaEvent.type) {
    case 'scan_started':
      console.log('🚀 Scan started for:', qaEvent.data.base_url);
      document.getElementById('status').textContent = 'Scanning...';
      break;
      
    case 'url_discovered':
      console.log('🔍 Found:', qaEvent.data.url);
      updateDiscoveredCount();
      break;
      
    case 'url_validated':
      if (qaEvent.data.valid) {
        console.log('✅ Valid:', qaEvent.data.url);
      } else {
        console.log('❌ Invalid (HTTP', qaEvent.data.status, '):', qaEvent.data.url);
      }
      break;
      
    case 'page_testing_started':
      console.log('🧪 Testing:', qaEvent.data.url);
      break;
      
    case 'page_analyzed':
      pagesAnalyzed++;
      avgScore += qaEvent.data.score;
      console.log(
        `📊 Analyzed (${pagesAnalyzed}):`,
        qaEvent.data.url,
        `Score: ${qaEvent.data.score}/100`
      );
      
      // Update dashboard
      updateWorstPages();
      updateCharts();
      break;
      
    case 'scan_completed':
      console.log('✨ Scan complete!');
      console.log('Summary:', qaEvent.data);
      avgScore /= pagesAnalyzed;
      document.getElementById('status').textContent = `Complete (Avg: ${avgScore.toFixed(1)}/100)`;
      ws.close();
      break;
      
    case 'scan_failed':
      console.error('❌ Scan failed:', qaEvent.data.error);
      ws.close();
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket connection closed');
};


═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 5: Scan Results with Event History
═══════════════════════════════════════════════════════════════════════════════

Request:
--------
curl http://localhost:8000/api/scan/scan_a1b2c3d4/events

Response (200):
---------------
{
  "scan_id": "scan_a1b2c3d4",
  "events": [
    {
      "type": "scan_started",
      "timestamp": "2026-01-16T12:30:45.123456Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "base_url": "https://httpbin.org"
      }
    },
    {
      "type": "url_discovered",
      "timestamp": "2026-01-16T12:30:46.234567Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "url": "https://httpbin.org/"
      }
    },
    {
      "type": "url_discovered",
      "timestamp": "2026-01-16T12:30:46.345678Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "url": "https://httpbin.org/html"
      }
    },
    {
      "type": "url_validated",
      "timestamp": "2026-01-16T12:30:48.456789Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "url": "https://httpbin.org/",
        "status": 200,
        "valid": true
      }
    },
    {
      "type": "page_testing_started",
      "timestamp": "2026-01-16T12:30:49.567890Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "url": "https://httpbin.org/"
      }
    },
    {
      "type": "page_analyzed",
      "timestamp": "2026-01-16T12:31:02.678901Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "url": "https://httpbin.org/",
        "page_type": "unknown",
        "score": 92.0
      }
    },
    {
      "type": "scan_completed",
      "timestamp": "2026-01-16T12:31:15.789012Z",
      "scan_id": "scan_a1b2c3d4",
      "data": {
        "total_discovered": 23,
        "total_valid": 18,
        "total_analyzed": 18,
        "avg_score": 91.5
      }
    }
  ]
}


═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 6: Python Script - Automated Scanning
═══════════════════════════════════════════════════════════════════════════════

import requests
import time
import json

def scan_and_report(url, timeout=300):
    \"\"\"Start a QA scan and wait for results.\"\"\"
    
    # Start scan
    print(f"Starting QA scan for {url}...")
    response = requests.post(
        'http://localhost:8000/api/scan',
        json={'url': url, 'mode': 'full'},
        timeout=10
    )
    
    if response.status_code != 202:
        print(f"Error: {response.status_code}")
        return
    
    scan_id = response.json()['scan_id']
    print(f"Scan ID: {scan_id}")
    
    # Poll for results
    start = time.time()
    while time.time() - start < timeout:
        result = requests.get(f'http://localhost:8000/api/scan/{scan_id}')
        data = result.json()
        
        status = data.get('status')
        progress = data.get('progress', 0)
        
        if status == 'completed':
            print(f"✅ Scan complete!")
            
            # Print results
            summary = data.get('summary', {})
            print(f"\nSummary:")
            print(f"  URLs discovered: {summary.get('totalDiscovered')}")
            print(f"  URLs analyzed: {summary.get('totalAnalyzed')}")
            print(f"  Average score: {summary.get('averageScore', 0):.1f}/100")
            print(f"  Critical issues: {summary.get('criticalIssues')}")
            print(f"  Total issues: {summary.get('totalIssues')}")
            
            # Print worst pages
            worst = data.get('worst_pages', [])
            if worst:
                print(f"\nWorst {len(worst)} pages:")
                for page in worst:
                    print(f"  {page['url']}")
                    print(f"    Score: {page['score']:.0f}/100")
                    print(f"    Issues: {page['totalIssueCount']}")
            
            return data
        
        elif status == 'failed':
            print(f"❌ Scan failed: {data.get('error')}")
            return
        
        else:
            print(f"Running... ({progress}%)")
            time.sleep(5)
    
    print("Timeout: Scan did not complete")

# Usage
scan_and_report('https://httpbin.org')


═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 7: Bash Script - CI/CD Integration
═══════════════════════════════════════════════════════════════════════════════

#!/bin/bash
# qa-scan.sh - Run QA scan and fail if critical issues found

TARGET_URL="${1:-https://example.com}"
API_URL="http://localhost:8000"
CRITICAL_THRESHOLD=5

echo "🔍 Starting QA scan for $TARGET_URL..."

# Start scan
RESPONSE=$(curl -s -X POST "$API_URL/api/scan" \\
  -H "Content-Type: application/json" \\
  -d "{\"url\":\"$TARGET_URL\",\"mode\":\"full\"}")

SCAN_ID=$(echo "$RESPONSE" | jq -r '.scan_id')
echo "Scan ID: $SCAN_ID"

# Wait for completion
MAX_WAIT=600  # 10 minutes
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
  STATUS=$(curl -s "$API_URL/api/scan/$SCAN_ID" | jq -r '.status')
  
  if [ "$STATUS" = "completed" ]; then
    echo "✅ Scan completed!"
    
    # Get results
    RESULT=$(curl -s "$API_URL/api/scan/$SCAN_ID")
    
    CRITICAL=$(echo "$RESULT" | jq -r '.summary.criticalIssues')
    AVERAGE=$(echo "$RESULT" | jq -r '.summary.averageScore')
    
    echo "Results:"
    echo "  Average Score: $AVERAGE/100"
    echo "  Critical Issues: $CRITICAL"
    
    if [ "$CRITICAL" -gt "$CRITICAL_THRESHOLD" ]; then
      echo "❌ FAILED: Too many critical issues ($CRITICAL > $CRITICAL_THRESHOLD)"
      exit 1
    else
      echo "✅ PASSED"
      exit 0
    fi
    
  elif [ "$STATUS" = "failed" ]; then
    ERROR=$(curl -s "$API_URL/api/scan/$SCAN_ID" | jq -r '.error')
    echo "❌ Scan failed: $ERROR"
    exit 2
  fi
  
  echo "Running... ($(( ELAPSED / 10 ))%)"
  sleep 10
  ELAPSED=$(( ELAPSED + 10 ))
done

echo "❌ TIMEOUT: Scan did not complete"
exit 3


═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 8: Standalone Python - Direct QA Analysis (No API)
═══════════════════════════════════════════════════════════════════════════════

import asyncio
from qa_engine.core import QAOrchestrator
from qa_engine.hygiene_transformer import (
    qa_results_to_hygiene_pages,
    qa_results_to_summary,
    qa_results_to_worst_pages
)

async def analyze_website(url):
    \"\"\"Run QA analysis directly without API.\"\"\"
    
    print(f"Analyzing {url}...")
    
    orchestrator = QAOrchestrator(
        base_url=url,
        max_pages=50,
        browser_concurrency=3
    )
    
    results = await orchestrator.run('standalone_scan')
    
    # Transform results
    pages = qa_results_to_hygiene_pages(results)
    summary = qa_results_to_summary(results)
    worst = qa_results_to_worst_pages(results, limit=5)
    
    # Print report
    print(f"\n{'='*70}")
    print(f"QA ANALYSIS REPORT: {url}")
    print(f"{'='*70}")
    
    print(f"\nSummary:")
    print(f"  Total Discovered: {summary['totalDiscovered']}")
    print(f"  Total Analyzed: {summary['totalAnalyzed']}")
    print(f"  Average Score: {summary['averageScore']:.1f}/100")
    print(f"  Critical Issues: {summary['criticalIssues']}")
    print(f"  Total Issues: {summary['totalIssues']}")
    
    print(f"\nWorst Performing Pages:")
    for i, page in enumerate(worst, 1):
        print(f"\\n  {i}. {page['url']}")
        print(f"     Score: {page['score']:.0f}/100")
        print(f"     Type: {page['type']}")
        print(f"     Issues: {page['totalIssueCount']} total, {page['criticalIssueCount']} critical")
        
        for issue in page['issues'][:3]:  # Show first 3 issues
            print(f"       - {issue['title']} ({issue['severity']})")
    
    print(f"\n{'='*70}")

# Run
asyncio.run(analyze_website('https://httpbin.org'))


═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 9: Custom Issue Detector
═══════════════════════════════════════════════════════════════════════════════

# In qa_engine/core/issue_detector.py, add to the detect() method:

    # Custom: Check for outdated jQuery
    html = page_data.get("raw_html", "")
    if '<script' in html:
        if 'jquery-1.' in html or 'jquery-2.' in html:
            issues.append(self._issue(
                url,
                "functional",
                "Outdated jQuery detected (v1 or v2)",
                "medium",
                details={"suggestion": "Update to jQuery 3.x+"}
            ))

Then run a scan:
    curl -X POST http://localhost:8000/api/scan \\
      -H "Content-Type: application/json" \\
      -d '{"url":"https://example.com","mode":"full"}'

The detector will automatically catch outdated jQuery usage.


═══════════════════════════════════════════════════════════════════════════════
EXAMPLE 10: View Detailed Issue Information
═══════════════════════════════════════════════════════════════════════════════

Request:
--------
curl http://localhost:8000/api/scan/scan_a1b2c3d4 | jq '.hygiene_pages[0]'

Response:
---------
{
  "url": "https://httpbin.org/",
  "type": "unknown",
  "score": 92.0,
  "criticalIssueCount": 0,
  "totalIssueCount": 2,
  "issues": [
    {
      "category": "performance",
      "title": "Heavy DOM (>4000 nodes)",
      "severity": "medium",
      "details": {}
    },
    {
      "category": "ui",
      "title": "Missing footer",
      "severity": "low",
      "details": {}
    }
  ]
}

This shows exactly what issues were detected and their severity.


═══════════════════════════════════════════════════════════════════════════════

For more examples and complete documentation, see:
  - QA_API_REFERENCE.md
  - QA_ENGINE_QUICKSTART.md
  - QA_ENGINE_EXTENSIONS.md
"""
