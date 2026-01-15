"""HTTP validator for URLs."""

import requests
import logging
from typing import Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


logger = logging.getLogger(__name__)


class URLValidator:
    """Validate URLs via HTTP requests."""
    
    def __init__(self, timeout: int = 5, max_workers: int = 50):
        """
        Initialize validator.
        
        Args:
            timeout: Request timeout in seconds
            max_workers: Max concurrent threads
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def validate_url(self, url: str) -> Tuple[str, int, int]:
        """
        Validate single URL via HTTP HEAD/GET.
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (url, status_code, content_length)
        """
        try:
            # Try HEAD first
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            content_length = len(response.content) if response.content else int(
                response.headers.get('Content-Length', 0)
            )
            return url, response.status_code, content_length
        except requests.Timeout:
            return url, 0, 0  # Timeout
        except requests.ConnectionError:
            return url, 0, 0  # Connection error
        except Exception as e:
            logger.debug(f"Error validating {url}: {str(e)}")
            return url, 0, 0
    
    def validate_batch(self, urls: list) -> Dict[str, Dict]:
        """
        Validate multiple URLs in parallel.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            Dict mapping URL to {status, content_length}
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.validate_url, url): url for url in urls}
            
            for future in as_completed(futures):
                try:
                    url, status, length = future.result()
                    results[url] = {
                        'status': status,
                        'content_length': length,
                        'alive': status in [200, 201, 202, 204, 206, 301, 302, 303, 307, 308]
                    }
                except Exception as e:
                    url = futures[future]
                    logger.debug(f"Validation failed for {url}: {str(e)}")
                    results[url] = {'status': 0, 'content_length': 0, 'alive': False}
        
        return results
    
    def check_alive(self, url: str) -> bool:
        """
        Quick check if URL is alive (not 404/500).
        
        Args:
            url: URL to check
            
        Returns:
            True if alive
        """
        status_code = self.validate_url(url)[1]
        return status_code in [200, 201, 202, 204, 206, 301, 302, 303, 307, 308]
    
    def close(self):
        """Close session."""
        self.session.close()
