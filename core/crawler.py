"""Live crawler for discovering URLs by following links."""

import requests
import logging
from typing import Set, Dict, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import normalize_url, is_internal_url, extract_domain


logger = logging.getLogger(__name__)


class LiveCrawler:
    """Crawl live websites to discover URLs."""
    
    def __init__(self, domain: str, depth: int = 3, timeout: int = 5, max_workers: int = 50):
        """
        Initialize crawler.
        
        Args:
            domain: Target domain
            depth: Crawl depth
            timeout: Request timeout
            max_workers: Max concurrent threads
        """
        self.domain = domain
        self.depth = depth
        self.timeout = timeout
        self.max_workers = max_workers
        self.visited = set()
        self.discovered_urls = set()
        self.js_files = {}
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def crawl(self) -> Dict[str, Set]:
        """
        Crawl domain starting from root.
        
        Returns:
            Dict with 'urls' and 'js_files' keys
        """
        # Ensure domain has scheme
        if not self.domain.startswith('http'):
            self.domain = f'https://{self.domain}'
        
        logger.info(f"Starting crawl of {self.domain} with depth {self.depth}")
        
        # Start crawl from root
        self._crawl_recursive(self.domain, 0)
        
        logger.info(f"Crawl complete. Found {len(self.discovered_urls)} URLs, {len(self.js_files)} JS files")
        
        return {
            'urls': self.discovered_urls,
            'js_files': self.js_files
        }
    
    def _crawl_recursive(self, url: str, current_depth: int):
        """
        Recursively crawl URL and discovered links.
        
        Args:
            url: URL to crawl
            current_depth: Current recursion depth
        """
        # Check depth limit
        if current_depth >= self.depth:
            return
        
        # Check if already visited
        url = normalize_url(url)
        if url in self.visited:
            return
        
        self.visited.add(url)
        
        # Check if internal
        if not is_internal_url(url, self.domain):
            return
        
        try:
            logger.debug(f"Crawling (depth {current_depth}): {url}")
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Add to discovered
            self.discovered_urls.add(url)
            
            # Parse content
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Handle HTML
            if 'text/html' in content_type:
                self._extract_urls_from_html(response.text, url, current_depth)
            
            # Store JS files for later parsing
            elif 'javascript' in content_type or url.endswith('.js'):
                self.js_files[url] = response.text
        
        except requests.Timeout:
            logger.debug(f"Timeout crawling {url}")
        except requests.RequestException as e:
            logger.debug(f"Error crawling {url}: {str(e)}")
        except Exception as e:
            logger.debug(f"Unexpected error crawling {url}: {str(e)}")
    
    def _extract_urls_from_html(self, html: str, base_url: str, current_depth: int):
        """
        Extract URLs from HTML content.
        
        Args:
            html: HTML content
            base_url: Base URL for relative path resolution
            current_depth: Current recursion depth
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract from <a href>
            for link in soup.find_all('a', href=True):
                url = link['href']
                if url:
                    self._process_found_url(url, base_url, current_depth)
            
            # Extract from <form action>
            for form in soup.find_all('form', action=True):
                url = form['action']
                if url:
                    self._process_found_url(url, base_url, current_depth)
            
            # Extract from <script src>
            for script in soup.find_all('script', src=True):
                url = script['src']
                if url:
                    self._process_found_url(url, base_url, current_depth)
            
            # Extract from <link href>
            for link in soup.find_all('link', href=True):
                url = link['href']
                if url:
                    self._process_found_url(url, base_url, current_depth)
            
            # Extract from meta refresh
            for meta in soup.find_all('meta', attrs={'http-equiv': 'refresh'}):
                content = meta.get('content', '')
                if 'url=' in content:
                    url = content.split('url=')[-1].strip('\'"')
                    if url:
                        self._process_found_url(url, base_url, current_depth)
        
        except Exception as e:
            logger.debug(f"Error parsing HTML: {str(e)}")
    
    def _process_found_url(self, url: str, base_url: str, current_depth: int):
        """
        Process discovered URL and add to queue if internal.
        
        Args:
            url: Discovered URL
            base_url: Base URL for resolution
            current_depth: Current depth
        """
        try:
            # Normalize
            normalized = normalize_url(url, base_url)
            
            if normalized and is_internal_url(normalized, self.domain):
                # Continue crawl
                self._crawl_recursive(normalized, current_depth + 1)
        
        except Exception as e:
            logger.debug(f"Error processing URL {url}: {str(e)}")
    
    def close(self):
        """Close session."""
        self.session.close()
