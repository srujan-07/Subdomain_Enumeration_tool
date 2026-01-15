# Quick Start Guide

Get up and running with the URL Enumeration Tool in 5 minutes!

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test basic functionality
python main.py --help
```

## First Enumeration

```bash
# Enumerate example.com (default settings)
python main.py -d example.com

# This will:
# - Live crawl the website
# - Extract endpoints from JavaScript
# - Query Wayback Machine for historical URLs
# - Brute force common paths
# - Parse robots.txt and sitemap.xml
# - Validate all URLs
# - Show summary statistics
```

## Common Use Cases

### 1. Quick Scan (2-3 minutes)
```bash
python main.py -d target.com --depth 2 --timeout 3 --threads 30
```

### 2. Thorough Scan (10-20 minutes)
```bash
python main.py -d target.com --depth 5 --threads 100 --timeout 10
```

### 3. Save Results to JSON
```bash
python main.py -d target.com --json -o results.json
```

### 4. Get Only Live URLs
```bash
python main.py -d target.com --only-alive
```

### 5. Debug Mode (see what's happening)
```bash
python main.py -d target.com --verbose
```

### 6. Specific Techniques Only
```bash
# Fast: Skip slow Wayback Machine
python main.py -d target.com --techniques live,js,bruteforce

# Passive only: Just query archives
python main.py -d target.com --techniques wayback
```

## Understanding Output

### Text Output (Default)
```
https://example.com/
https://example.com/about
https://example.com/admin
https://example.com/api/users
...
```

### JSON Output (-—json flag)
```json
{
  "urls": [...],
  "summary": {
    "total_urls": 350,
    "alive_urls": 280,
    "sources_used": ["live_crawl", "js_analysis"],
    "sources_summary": {...}
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

### Summary Output
```
======================================================================
ENUMERATION SUMMARY
======================================================================
Domain: example.com
Total URLs Found: 350
Alive URLs: 280
Techniques Used: live_crawl, js_analysis, wayback, bruteforce

URLs by Source:
  live_crawl: 120
  js_analysis: 85
  wayback: 130
  bruteforce: 15
======================================================================
```

## Parameter Tuning

| Parameter | Default | Good For | Description |
|-----------|---------|----------|-------------|
| `--depth` | 3 | Most sites | How deep to crawl (1-5 typical) |
| `--threads` | 50 | Balanced | Concurrent requests (10-100+) |
| `--timeout` | 5s | Medium | Request timeout (3-10s) |

### Adjust for Your Target

**Fast Network / Large Site:**
```bash
python main.py -d target.com --threads 200 --depth 5 --timeout 3
```

**Slow Network / Rate Limiting:**
```bash
python main.py -d target.com --threads 10 --depth 2 --timeout 10
```

**Limited Time:**
```bash
python main.py -d target.com --techniques live,js --threads 100
```

## Troubleshooting

### "Too many requests" errors
- **Solution**: Reduce `--threads` to 10-20
- Try: `python main.py -d target.com --threads 10`

### "Connection timeout" errors
- **Solution**: Increase `--timeout` to 10
- Try: `python main.py -d target.com --timeout 10`

### No URLs found
- **Check**: Is the domain correct?
- **Try**: `python main.py -d target.com --verbose` (to debug)
- **Try**: `python main.py -d target.com --techniques wayback` (if site is new)

### Want to see what's happening?
- **Use**: `python main.py -d target.com --verbose`

## File Outputs

### Save to TXT
```bash
python main.py -d target.com -o urls.txt
```
Creates `urls.txt` with one URL per line.

### Save to JSON
```bash
python main.py -d target.com --json -o results.json
```
Creates `results.json` with detailed metadata.

## Tips & Tricks

### 1. Combine with other tools
```bash
# Get URLs and feed to another tool
python main.py -d target.com --silent | grep api | head -50

# Save for later processing
python main.py -d target.com --silent > urls.txt

# Filter only admin pages
python main.py -d target.com --silent | grep admin
```

### 2. Monitor progress
```bash
# Verbose output shows what's being crawled
python main.py -d target.com --verbose | grep -i discovered
```

### 3. Compare results
```bash
# Run with different techniques and compare
python main.py -d target.com --techniques live,js > results1.txt
python main.py -d target.com --techniques wayback > results2.txt

# Find unique URLs
diff results1.txt results2.txt
```

### 4. Focus on specific endpoints
```bash
# Get all results then filter
python main.py -d target.com --silent | grep /api/

# Save only admin/login pages
python main.py -d target.com --silent | grep -E '(admin|login|user)' > admin_urls.txt
```

## Real-World Examples

### Penetration Test
```bash
# Full enumeration with all techniques
python main.py -d internalapp.company.com \
  --depth 4 \
  --threads 100 \
  --only-alive \
  --json -o pentest_results.json
```

### Bug Bounty
```bash
# Quick scan to find entry points
python main.py -d bugbounty-target.com \
  --depth 3 \
  --threads 50 \
  --techniques live,js,wayback \
  --silent | head -100
```

### Source Code Review
```bash
# Find all endpoints then cross-check with code
python main.py -d app.company.com \
  --only-alive \
  -o live_endpoints.json
```

## Next Steps

1. **Explore Results**
   - Review the discovered URLs
   - Look for interesting endpoints (api, admin, test, backup, etc.)

2. **Investigate Findings**
   - Use the URLs in further security testing
   - Check status codes and response sizes
   - Identify unusual or sensitive endpoints

3. **Refine Search**
   - Adjust parameters based on results
   - Try specific technique combinations
   - Use filters for targeted discovery

4. **Integrate with Workflow**
   - Export results for team collaboration
   - Feed URLs to vulnerability scanners
   - Track changes over time

---

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Run `python main.py --help` for all options
- Enable `--verbose` flag for debugging
- Review error messages carefully

---

**You're ready to enumerate! 🚀**
