"""Brute force common paths using wordlist."""

import logging
from typing import Set, List
from .utils import get_wordlist


logger = logging.getLogger(__name__)


class BruteForcer:
    """Brute force common URLs using wordlist."""
    
    def __init__(self, custom_wordlist: List[str] = None):
        """
        Initialize brute forcer.
        
        Args:
            custom_wordlist: Custom wordlist (uses default if None)
        """
        self.wordlist = custom_wordlist if custom_wordlist else get_wordlist()
        self.extensions = ['.php', '.html', '.jsp', '.aspx', '.json', '.xml', '.api']
    
    def generate_paths(self) -> List[str]:
        """
        Generate common paths to test.
        
        Args:
            None
            
        Returns:
            List of paths
        """
        paths = set()
        
        for word in self.wordlist:
            # Base path
            paths.add(f'/{word}')
            
            # With extensions
            for ext in self.extensions:
                paths.add(f'/{word}{ext}')
            
            # Nested paths
            paths.add(f'/{word}/')
            paths.add(f'/api/{word}')
            paths.add(f'/v1/{word}')
            paths.add(f'/v2/{word}')
        
        return sorted(list(paths))
    
    def generate_urls(self, domain: str) -> List[str]:
        """
        Generate full URLs for a domain.
        
        Args:
            domain: Target domain
            
        Returns:
            List of full URLs
        """
        # Ensure domain has scheme
        if not domain.startswith('http'):
            domain = f'https://{domain}'
        
        paths = self.generate_paths()
        urls = [f"{domain.rstrip('/')}{path}" for path in paths]
        
        logger.info(f"Generated {len(urls)} URLs for brute force testing")
        return urls
    
    def get_wordlist_stats(self) -> dict:
        """
        Get wordlist statistics.
        
        Returns:
            Dict with stats
        """
        return {
            'words': len(self.wordlist),
            'extensions': len(self.extensions),
            'estimated_urls': len(self.wordlist) * (2 + len(self.extensions) + 3),
        }
