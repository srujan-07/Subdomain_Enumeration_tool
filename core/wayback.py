"""Wayback Machine integration for historical URL discovery."""

import requests
import logging
from typing import Set
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


class WaybackMachine:
    """Query Wayback Machine CDX API for historical URLs."""
    
    CDX_API_URL = "https://web.archive.org/cdx/search/cdx"
    TIMEOUT = 10
    
    def __init__(self):
        """Initialize Wayback Machine client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search(self, domain: str, limit: int = 10000) -> Set[str]:
        """
        Search Wayback Machine CDX API for URLs.
        
        Args:
            domain: Target domain (e.g., 'example.com')
            limit: Max results to fetch
            
        Returns:
            Set of discovered URLs
        """
        urls = set()
        
        # Clean domain
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        
        try:
            params = {
                'url': f'{domain}/*',
                'matchType': 'domain',
                'output': 'json',
                'collapse': 'statuscode',
                'limit': limit,
                'from': '20100101',
                'to': '20261231'
            }
            
            logger.info(f"Querying Wayback Machine for {domain}")
            response = self.session.get(
                self.CDX_API_URL,
                params=params,
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) > 1:
                # First row is headers, rest are results
                for row in data[1:]:
                    if len(row) >= 3:
                        timestamp = row[1]
                        url = row[2]
                        
                        if url and url.startswith('http'):
                            urls.add(url)
            
            logger.info(f"Found {len(urls)} historical URLs from Wayback Machine")
            
        except requests.Timeout:
            logger.warning("Wayback Machine request timed out")
        except requests.RequestException as e:
            logger.warning(f"Wayback Machine API error: {str(e)}")
        except Exception as e:
            logger.debug(f"Error parsing Wayback Machine response: {str(e)}")
        
        return urls
    
    def search_multiple_domains(self, domains: list) -> Set[str]:
        """
        Search multiple domains.
        
        Args:
            domains: List of domains
            
        Returns:
            Combined set of URLs
        """
        all_urls = set()
        for domain in domains:
            try:
                urls = self.search(domain)
                all_urls.update(urls)
            except Exception as e:
                logger.debug(f"Error searching {domain}: {str(e)}")
        
        return all_urls
    
    def close(self):
        """Close session."""
        self.session.close()
