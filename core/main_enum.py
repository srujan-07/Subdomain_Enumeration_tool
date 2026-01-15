"""Main orchestrator that combines all discovery techniques."""

import logging
import json
from typing import Dict, Set, List
from .crawler import LiveCrawler
from .js_parser import JSParser
from .wayback import WaybackMachine
from .bruteforce import BruteForcer
from .validator import URLValidator
from .utils import normalize_url, is_internal_url, deduplicate_urls, get_status_tag
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


class URLEnumerator:
    """Orchestrate all URL discovery techniques."""
    
    def __init__(self, domain: str, depth: int = 3, timeout: int = 5, 
                 threads: int = 50, only_alive: bool = False):
        """
        Initialize enumerator.
        
        Args:
            domain: Target domain
            depth: Crawl depth
            timeout: Request timeout
            threads: Max concurrent threads
            only_alive: Only return alive URLs
        """
        self.domain = domain
        self.depth = depth
        self.timeout = timeout
        self.threads = threads
        self.only_alive = only_alive
        
        self.all_urls = {}  # {url: {status, source, ...}}
        self.sources_summary = {}
    
    def enumerate(self, techniques: List[str] = None) -> Dict:
        """
        Run complete enumeration using specified techniques.
        
        Args:
            techniques: List of techniques to use. Default: all
                       ['live', 'js', 'wayback', 'bruteforce', 'robots', 'sitemap']
        
        Returns:
            Dict with results
        """
        if techniques is None:
            techniques = ['live', 'js', 'wayback', 'bruteforce', 'robots', 'sitemap']
        
        logger.info(f"Starting enumeration of {self.domain}")
        logger.info(f"Techniques: {', '.join(techniques)}")
        
        # Live crawling
        if 'live' in techniques:
            self._run_live_crawling()
        
        # JavaScript analysis
        if 'js' in techniques:
            self._run_js_analysis()
        
        # Wayback Machine
        if 'wayback' in techniques:
            self._run_wayback()
        
        # Robots & Sitemap
        if 'robots' in techniques or 'sitemap' in techniques:
            self._run_robots_and_sitemap()
        
        # Brute force
        if 'bruteforce' in techniques:
            self._run_bruteforce()
        
        # Validate all URLs
        self._validate_urls()
        
        return self._get_results()
    
    def _run_live_crawling(self):
        """Run live website crawler."""
        logger.info("Running live crawling...")
        try:
            crawler = LiveCrawler(
                self.domain,
                depth=self.depth,
                timeout=self.timeout,
                max_workers=self.threads
            )
            
            result = crawler.crawl()
            
            for url in result['urls']:
                self._add_url(url, 'live_crawl')
            
            # Store JS files for later analysis
            if result['js_files']:
                self._js_files_from_crawler = result['js_files']
            
            crawler.close()
            self.sources_summary['live_crawl'] = len(result['urls'])
            
        except Exception as e:
            logger.error(f"Live crawling error: {str(e)}")
    
    def _run_js_analysis(self):
        """Run JavaScript analysis."""
        logger.info("Running JavaScript analysis...")
        try:
            parser = JSParser()
            
            # Get JS files from crawler if available
            js_files = getattr(self, '_js_files_from_crawler', {})
            
            endpoints = parser.extract_from_js_files(js_files)
            
            # Convert endpoints to full URLs
            for endpoint in endpoints:
                url = f"{self.domain.rstrip('/')}{endpoint}" if not self.domain.startswith('http') else f"{self.domain.rstrip('/')}{endpoint}"
                if not url.startswith('http'):
                    url = f"https://{url}"
                self._add_url(normalize_url(url), 'js_analysis')
            
            self.sources_summary['js_analysis'] = len(endpoints)
            
        except Exception as e:
            logger.error(f"JavaScript analysis error: {str(e)}")
    
    def _run_wayback(self):
        """Query Wayback Machine."""
        logger.info("Running Wayback Machine search...")
        try:
            wayback = WaybackMachine()
            
            domain_clean = self.domain.replace('http://', '').replace('https://', '').replace('www.', '')
            urls = wayback.search(domain_clean)
            
            for url in urls:
                if is_internal_url(url, self.domain):
                    self._add_url(normalize_url(url), 'wayback')
            
            wayback.close()
            self.sources_summary['wayback'] = len(urls)
            
        except Exception as e:
            logger.error(f"Wayback Machine error: {str(e)}")
    
    def _run_robots_and_sitemap(self):
        """Parse robots.txt and sitemap.xml."""
        logger.info("Parsing robots.txt and sitemap.xml...")
        try:
            base = self.domain if self.domain.startswith('http') else f'https://{self.domain}'
            base = base.rstrip('/')
            
            # Parse robots.txt
            robots_found = self._parse_robots_txt(f'{base}/robots.txt')
            self.sources_summary['robots'] = robots_found
            
            # Parse sitemaps
            sitemap_found = self._parse_sitemap(f'{base}/sitemap.xml')
            self.sources_summary['sitemap'] = sitemap_found
            
        except Exception as e:
            logger.error(f"Robots/Sitemap error: {str(e)}")
    
    def _parse_robots_txt(self, url: str) -> int:
        """Parse robots.txt for disallowed paths."""
        import requests
        count = 0
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.startswith('Disallow:') or line.startswith('Allow:'):
                        path = line.split(':', 1)[-1].strip()
                        if path and path != '/':
                            self._add_url(normalize_url(f"{self.domain.rstrip('/')}{path}"), 'robots')
                            count += 1
        except Exception as e:
            logger.debug(f"Error parsing robots.txt: {str(e)}")
        return count
    
    def _parse_sitemap(self, url: str) -> int:
        """Parse sitemap.xml for URLs."""
        import requests
        import xml.etree.ElementTree as ET
        count = 0
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                try:
                    root = ET.fromstring(response.content)
                    
                    # Handle both sitemap and sitemapindex
                    for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                        if url_elem.text:
                            self._add_url(normalize_url(url_elem.text), 'sitemap')
                            count += 1
                    
                    # If it's a sitemap index, fetch nested sitemaps
                    for sitemap_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                        if sitemap_elem.text:
                            try:
                                nested_response = requests.get(sitemap_elem.text, timeout=self.timeout)
                                if nested_response.status_code == 200:
                                    nested_root = ET.fromstring(nested_response.content)
                                    for url_elem in nested_root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                                        if url_elem.text:
                                            self._add_url(normalize_url(url_elem.text), 'sitemap')
                                            count += 1
                            except Exception:
                                pass
                
                except ET.ParseError:
                    logger.debug("Could not parse sitemap XML")
        
        except Exception as e:
            logger.debug(f"Error parsing sitemap: {str(e)}")
        
        return count
    
    def _run_bruteforce(self):
        """Brute force common paths."""
        logger.info("Running brute force...")
        try:
            bruteforcer = BruteForcer()
            urls = bruteforcer.generate_urls(self.domain)
            
            # Add all to list (will validate later)
            for url in urls:
                self._add_url(normalize_url(url), 'bruteforce')
            
            self.sources_summary['bruteforce'] = len(urls)
            
        except Exception as e:
            logger.error(f"Brute force error: {str(e)}")
    
    def _validate_urls(self):
        """Validate all discovered URLs."""
        logger.info(f"Validating {len(self.all_urls)} URLs...")
        
        urls_to_validate = list(self.all_urls.keys())
        
        try:
            validator = URLValidator(timeout=self.timeout, max_workers=self.threads)
            results = validator.validate_batch(urls_to_validate)
            
            for url, validation in results.items():
                if url in self.all_urls:
                    self.all_urls[url]['status'] = validation['status']
                    self.all_urls[url]['content_length'] = validation['content_length']
                    self.all_urls[url]['alive'] = validation['alive']
            
            validator.close()
        
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
    
    def _add_url(self, url: str, source: str):
        """Add URL to results."""
        if not url or not is_internal_url(url, self.domain):
            return
        
        url = normalize_url(url)
        
        if url not in self.all_urls:
            self.all_urls[url] = {
                'sources': set(),
                'status': None,
                'content_length': 0,
                'alive': False
            }
        
        self.all_urls[url]['sources'].add(source)
    
    def _get_results(self) -> Dict:
        """Format and return results."""
        # Filter by alive if requested
        urls = list(self.all_urls.keys())
        if self.only_alive:
            urls = [u for u in urls if self.all_urls[u].get('alive', False)]
        
        # Sort
        urls = sorted(urls)
        
        # Format results
        results = {
            'urls': urls,
            'url_details': {},
            'summary': {
                'total_urls': len(urls),
                'alive_urls': sum(1 for u in urls if self.all_urls[u].get('alive', False)),
                'sources_used': list(self.sources_summary.keys()),
                'sources_summary': self.sources_summary
            }
        }
        
        # Add details
        for url in urls:
            details = self.all_urls[url]
            results['url_details'][url] = {
                'status': details.get('status'),
                'status_tag': get_status_tag(details.get('status', 0)),
                'content_length': details.get('content_length', 0),
                'alive': details.get('alive', False),
                'sources': sorted(list(details['sources']))
            }
        
        return results
