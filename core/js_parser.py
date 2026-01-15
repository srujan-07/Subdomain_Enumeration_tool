"""JavaScript file analysis for endpoint extraction."""

import re
import logging
from typing import Set
from .utils import extract_regex_matches


logger = logging.getLogger(__name__)


class JSParser:
    """Extract endpoints from JavaScript files."""
    
    # Regex patterns for endpoint detection
    PATTERNS = [
        # API endpoints with quotes
        r'["\']([/a-zA-Z0-9_\-./]+(?:\.(?:php|jsp|aspx|html|json|xml|api)))["\']',
        # Fetch/XHR calls
        r'fetch\(["\']([^"\']+)["\']',
        r'axios\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        r'XMLHttpRequest\(\).*?open\(["\'](?:GET|POST)["\'],\s*["\']([^"\']+)["\']',
        # URL in string literals
        r'["\']([/a-zA-Z0-9_\-./]+/(?:api|v\d+|admin|users|data|config)[/a-zA-Z0-9_\-./]*)["\']',
        # Trailing .php, .jsp, .aspx
        r'["\']([/a-zA-Z0-9_\-./]+\.(?:php|jsp|aspx|html))["\']',
        # URL patterns with /api
        r'["\']([/a-zA-Z0-9_\-./]*/?api[/a-zA-Z0-9_\-./]*)["\']',
        # Double slash paths
        r'(?:^|["\'])\s*(/[a-zA-Z0-9_\-./]+)\s*(?:["\']|$)',
    ]
    
    def __init__(self):
        """Initialize JS parser."""
        self.parsed_count = 0
        self.endpoints_found = 0
    
    def extract_endpoints(self, js_content: str) -> Set[str]:
        """
        Extract endpoints from JavaScript content.
        
        Args:
            js_content: JavaScript source code
            
        Returns:
            Set of discovered endpoints
        """
        endpoints = set()
        
        try:
            # Extract using patterns
            matches = extract_regex_matches(js_content, self.PATTERNS)
            
            for match in matches:
                endpoint = match.strip()
                
                # Filter valid endpoints
                if self._is_valid_endpoint(endpoint):
                    endpoints.add(endpoint)
                    self.endpoints_found += 1
            
            self.parsed_count += 1
            
        except Exception as e:
            logger.debug(f"Error parsing JavaScript: {str(e)}")
        
        return endpoints
    
    @staticmethod
    def _is_valid_endpoint(endpoint: str) -> bool:
        """
        Validate if string is a valid endpoint.
        
        Args:
            endpoint: Potential endpoint string
            
        Returns:
            True if valid
        """
        # Must start with /
        if not endpoint.startswith('/'):
            return False
        
        # Remove common false positives
        invalid_patterns = [
            r'^\s*$',  # Empty
            r'\.jpg|\.png|\.gif|\.css|\.woff',  # Media files
            r'^//$',  # Just slashes
            r'^\s+',  # Just whitespace
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, endpoint, re.IGNORECASE):
                return False
        
        # Must have reasonable length
        return 1 < len(endpoint) < 500
    
    def extract_from_js_files(self, js_files: dict) -> Set[str]:
        """
        Extract endpoints from multiple JS file contents.
        
        Args:
            js_files: Dict mapping URL to JS content
            
        Returns:
            Set of all discovered endpoints
        """
        all_endpoints = set()
        
        for url, content in js_files.items():
            try:
                endpoints = self.extract_endpoints(content)
                all_endpoints.update(endpoints)
                logger.debug(f"Extracted {len(endpoints)} endpoints from {url}")
            except Exception as e:
                logger.debug(f"Failed to parse {url}: {str(e)}")
        
        return all_endpoints
