# URL Enumeration Tool

Complete Python CLI tool that discovers **ALL possible pages/URLs** of a given domain, combining the capabilities of **hakrawler**, **gau**, and **waybackurls**.

## ⚠️ DISCLAIMER

**THIS TOOL IS FOR AUTHORIZED SECURITY TESTING AND RECONNAISSANCE ONLY!**

- **LEGAL NOTICE**: Only use this tool on domains you own or have explicit written permission to test
- **ETHICAL USAGE**: This tool is designed for legitimate security auditing, penetration testing, and bug bounty hunting
- **NO WARRANTY**: The authors assume no liability for any damage caused by misuse
- **TERMS**: By using this tool, you agree to use it responsibly and in compliance with all applicable laws

Unauthorized access to computer systems is illegal. Use this tool only on systems you have permission to test.

---

## Features

### 🎯 Multi-Technique URL Discovery

1. **Live Crawling**
   - Crawls website starting from root URL
   - Follows internal links with configurable depth
   - Parses HTML elements: `<a href>`, `<form action>`, `<script src>`, `<link href>`
   - Avoids infinite loops with visited URL tracking
   - Normalizes URLs and handles relative paths

2. **JavaScript Analysis**
   - Downloads and analyzes JavaScript files from crawled pages
   - Extracts API endpoints using regex patterns
   - Discovers endpoints in fetch(), axios(), XMLHttpRequest() calls
   - Finds patterns: `/api/*`, `.php`, `.jsp`, `.aspx`, `.html` files

3. **Wayback Machine Integration**
   - Queries Wayback CDX API for historical URLs
   - Discovers archived pages and endpoints
   - Completely passive (no target server requests)
   - Automatically deduplicates results

4. **Common Path Brute Force**
   - Uses built-in wordlist of common paths (admin, login, api, etc.)
   - Tests variations: `/word`, `/word.php`, `/word/`, `/api/word`, `/v1/word`, etc.
   - Validates via HTTP requests
   - 40+ common path patterns tested

5. **robots.txt & sitemap.xml Parsing**
   - Extracts disallowed/allowed paths from robots.txt
   - Parses sitemap.xml for published URLs
   - Follows nested sitemap indices
   - Discovers both obfuscated and public endpoints

### 🚀 Performance Features

- **Multi-threaded**: Concurrent requests using ThreadPoolExecutor (default 50 workers)
- **Configurable concurrency**: Scale up/down based on target capacity
- **Smart rate limiting**: Respects timeouts and server responses
- **Efficient deduplication**: Global URL deduplication across all sources
- **Smart validation**: Parallel HTTP validation of all discovered URLs

### 📊 Output Formats

- **Plain Text**: One URL per line (default)
- **JSON**: Structured output with metadata
  - URL status codes
  - Source discovery method
  - Content length
  - Alive/Dead status

### 🛠️ Advanced Options

- `--depth <n>`: Control crawl depth (default 3)
- `--threads <n>`: Adjust worker count (default 50)
- `--timeout <sec>`: Request timeout (default 5s)
- `--only-alive`: Filter to HTTP 200/3xx only
- `--silent`: Output URLs only, no summary
- `--techniques`: Choose specific discovery methods
- Verbose logging for troubleshooting

---

## Installation

### Requirements
- Python 3.7+
- pip

### Setup

```bash
# Clone/download the tool
cd Subdomain_Enumeration_tool

# Install dependencies
pip install -r requirements.txt

# Make executable (Linux/Mac)
chmod +x main.py
```

---

## Usage

### Basic Usage

```bash
python main.py -d example.com
```

### Common Scenarios

**1. Quick enumeration with all techniques:**
```bash
python main.py -d example.com --depth 3 --threads 50
```

**2. Only live, reachable URLs:**
```bash
python main.py -d example.com --only-alive
```

**3. Deep crawl with high concurrency:**
```bash
python main.py -d example.com --depth 5 --threads 100
```

**4. JSON output to file:**
```bash
python main.py -d example.com --json -o results.json
```

**5. Specific techniques only:**
```bash
python main.py -d example.com --techniques live,js,wayback
```

**6. Silent mode (URLs only):**
```bash
python main.py -d example.com --silent > urls.txt
```

**7. Test with longer timeout:**
```bash
python main.py -d example.com --timeout 10
```

**8. Verbose debugging:**
```bash
python main.py -d example.com --verbose
```

---

## Command-Line Options

```
usage: main.py [-h] -d DOMAIN [--depth DEPTH] [--threads THREADS]
               [--timeout TIMEOUT] [--json] [--txt] [-o OUTPUT] [--silent]
               [--only-alive] [--techniques TECHNIQUES] [-v] [-q]

Complete URL/Page Enumeration Tool

options:
  -h, --help              Show this help message
  -d, --domain DOMAIN     Target domain (required) [e.g., example.com]
  
  --depth DEPTH          Crawl depth for live crawling (default: 3)
  --threads THREADS      Number of concurrent threads (default: 50)
  --timeout TIMEOUT      Request timeout in seconds (default: 5)
  
  --json                 Output results in JSON format
  --txt                  Output results in TXT format (default)
  -o, --output OUTPUT    Save results to file
  
  --silent               Only print URLs, no summary
  --only-alive           Only return HTTP 200/3xx responses
  --techniques TECH      Comma-separated discovery methods
                        (Options: live,js,wayback,bruteforce,robots,sitemap)
  
  -v, --verbose         Enable debug logging
  -q, --quiet           Suppress logging, show URLs only
```

---

## Project Structure

```
├── main.py                  # Entry point
├── cli.py                   # CLI interface and argument parsing
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── core/
    ├── __init__.py          # Package initialization
    ├── main_enum.py         # Main orchestrator
    ├── crawler.py           # Live website crawler
    ├── js_parser.py         # JavaScript endpoint extraction
    ├── wayback.py           # Wayback Machine integration
    ├── bruteforce.py        # Common path brute force
    ├── validator.py         # HTTP URL validation
    └── utils.py             # Utility functions
```

---

## How It Works

### Discovery Pipeline

1. **Live Crawling**
   - Starts from `https://domain`
   - Follows all internal links up to specified depth
   - Extracts URLs from HTML elements
   - Collects JavaScript files for analysis

2. **JavaScript Analysis**
   - Parses all collected JS files
   - Extracts API endpoints and routes
   - Adds discovered endpoints to results

3. **Wayback Machine**
   - Queries historical URLs from Internet Archive
   - Discovers deprecated/moved endpoints
   - Completely passive

4. **Brute Force**
   - Tests common path patterns
   - Uses wordlist of typical paths
   - Validates existence via HTTP

5. **Robots & Sitemap**
   - Parses robots.txt for disallowed paths
   - Extracts all URLs from sitemap.xml
   - Follows nested sitemap indices

6. **Validation**
   - All discovered URLs validated via HEAD/GET
   - Status codes captured (200, 301, 403, 404, timeout, etc.)
   - Dead URLs tagged appropriately

### Output

Results include:
- Complete list of discovered URLs
- HTTP status codes
- Discovery source(s) for each URL
- Summary statistics
- Alive vs dead URL counts

---

## Examples

### Example 1: Complete scan
```bash
$ python main.py -d cvr.ac.in --depth 3 --threads 50

======================================================================
URL Enumeration Tool Started
======================================================================
2024-01-15 10:30:45 - core.main_enum - INFO - Starting enumeration of cvr.ac.in
2024-01-15 10:30:45 - core.main_enum - INFO - Techniques: live, js, wayback, bruteforce, robots, sitemap
2024-01-15 10:30:45 - core.crawler - INFO - Starting crawl of https://cvr.ac.in with depth 3
...
2024-01-15 10:31:30 - core.main_enum - INFO - Validating 2350 URLs...

======================================================================
ENUMERATION SUMMARY
======================================================================
Domain: cvr.ac.in
Total URLs Found: 1847
Alive URLs: 1253
Techniques Used: live_crawl, js_analysis, wayback, bruteforce, robots, sitemap

URLs by Source:
  live_crawl: 342
  js_analysis: 189
  wayback: 561
  bruteforce: 45
  robots: 28
  sitemap: 742
======================================================================

https://cvr.ac.in/
https://cvr.ac.in/about
https://cvr.ac.in/admin
https://cvr.ac.in/api/users
...
```

### Example 2: JSON output
```bash
python main.py -d example.com --json -o results.json
```

Results file structure:
```json
{
  "urls": [
    "https://example.com/",
    "https://example.com/about",
    "https://example.com/admin"
  ],
  "summary": {
    "total_urls": 350,
    "alive_urls": 280,
    "sources_used": ["live_crawl", "js_analysis", "wayback"],
    "sources_summary": {
      "live_crawl": 120,
      "js_analysis": 85,
      "wayback": 145
    }
  },
  "details": {
    "https://example.com/": {
      "status": 200,
      "status_tag": "[200]",
      "content_length": 45230,
      "alive": true,
      "sources": ["live_crawl"]
    }
  }
}
```

---

## Performance Tips

### For Large Targets

```bash
# High concurrency for fast networks
python main.py -d example.com --threads 200 --depth 4

# Lower timeout for faster enumeration
python main.py -d example.com --timeout 3

# Specific techniques only (skip slow ones)
python main.py -d example.com --techniques live,js
```

### For Rate-Limited Targets

```bash
# Lower concurrency and higher timeout
python main.py -d example.com --threads 10 --timeout 10

# Skip wayback and brute force (faster)
python main.py -d example.com --techniques live,js,robots,sitemap
```

---

## Troubleshooting

### "Connection timeout" errors
- Increase `--timeout` value
- Reduce `--threads` for rate limiting

### "Too many open files"
- Reduce `--threads` value

### Missing URLs from crawl
- Increase `--depth` for deeper crawling
- Check if site requires authentication
- Try with `--verbose` to see what's being crawled

### No results from Wayback
- Domain may not be in Internet Archive
- Use `--techniques live,js,bruteforce` to skip Wayback

---

## API Reference

### URLEnumerator

Main orchestrator class for discovery:

```python
from core.main_enum import URLEnumerator

enumerator = URLEnumerator(
    domain='example.com',
    depth=3,
    timeout=5,
    threads=50,
    only_alive=False
)

results = enumerator.enumerate(
    techniques=['live', 'js', 'wayback', 'bruteforce', 'robots', 'sitemap']
)
```

### LiveCrawler

For live crawling only:

```python
from core.crawler import LiveCrawler

crawler = LiveCrawler(
    domain='example.com',
    depth=3,
    timeout=5,
    max_workers=50
)

result = crawler.crawl()
crawler.close()
```

---

## Contributing

Improvements welcome! Areas for enhancement:
- Additional discovery techniques (DNS, CSP analysis, etc.)
- Better JavaScript endpoint detection
- Custom wordlist support
- Proxy support
- Authentication handling

---

## License

This tool is provided as-is for educational and authorized security testing purposes only.

---

## Disclaimer (IMPORTANT!)

⚠️ **READ BEFORE USE** ⚠️

This tool is designed for:
- ✅ Security researchers testing their own infrastructure
- ✅ Penetration testers with written client authorization
- ✅ Bug bounty hunters operating under program rules
- ✅ System administrators auditing their own networks

This tool is NOT for:
- ❌ Unauthorized access to any systems
- ❌ Illegal hacking or cyber attacks
- ❌ Scanning networks without permission
- ❌ Any activity violating laws or regulations

**The authors are NOT responsible for any damage caused by misuse of this tool.**

By using this tool, you agree to:
1. Only use it on systems you own or have explicit permission to test
2. Comply with all applicable laws and regulations
3. Not use it for any illegal purposes
4. Accept full responsibility for your actions

---

## Contact & Support

For issues, questions, or feature requests:
- Check existing issues and documentation
- Enable `--verbose` for debug output
- Review error messages carefully

---

**Happy hunting! 🔍**

---

## QA Bug & Hygiene Discovery Engine (Playwright)

An autonomous AI-driven web testing engine that crawls a site, loads each HTTP 200 page in Chromium via Playwright, and produces a JSON hygiene report with detected issues, page classification, and a global score.

### Install (QA engine only)
```bash
pip install -r qa_engine/requirements.txt
python -m playwright install chromium
```

### Run
```bash
python qa_engine/main.py https://example.com \
   -o qa_report.json \
   --max-pages 50 \
   --concurrency 10 \
   --browser-concurrency 3
```

### What it does
- Crawls internal links (httpx + BeautifulSoup) and keeps HTTP 200 HTML pages.
- For each page: Playwright captures DOM snapshot, console logs, network failures, performance metrics, accessibility tree.
- Structural analysis: header/footer/nav presence, repeated classes, simple broken link/image heuristics.
- Page classification: login, dashboard, list, form, wizard, report (DOM heuristics).
- Issue detection: JS errors, failed requests, missing structural elements, broken links/images, slow loads, heavy DOM, accessibility/name gaps, placeholder text.
- Knowledge graph: Page → Issues; hygiene scoring (base 100 minus severity weights) plus global score.

### Output
- JSON at the path you choose (default `qa_report.json`) with per-page summaries, issues, scores, and global hygiene score.
