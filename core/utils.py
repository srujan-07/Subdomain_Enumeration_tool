"""Utility functions for URL enumeration tool."""

import re
from urllib.parse import urljoin, urlparse, urlunparse
from typing import List, Set


def normalize_url(url: str, base_url: str = None) -> str:
    """
    Normalize a URL by removing fragments and resolving relative paths.
    
    Args:
        url: URL to normalize
        base_url: Base URL for relative URL resolution
        
    Returns:
        Normalized URL
    """
    if not url:
        return ""
    
    # Remove fragment
    url = url.split('#')[0].strip()
    
    if not url:
        return ""
    
    # Handle relative URLs
    if base_url and not url.startswith('http'):
        url = urljoin(base_url, url)
    
    # Ensure URL has scheme
    if not url.startswith('http'):
        url = 'https://' + url
    
    # Parse and normalize
    try:
        parsed = urlparse(url)
        
        # Remove default ports and trailing slashes
        netloc = parsed.netloc
        if parsed.scheme == 'https' and netloc.endswith(':443'):
            netloc = netloc[:-4]
        elif parsed.scheme == 'http' and netloc.endswith(':80'):
            netloc = netloc[:-3]
        
        # Reconstruct URL
        path = parsed.path if parsed.path else '/'
        query = f"?{parsed.query}" if parsed.query else ""
        
        normalized = f"{parsed.scheme}://{netloc}{path}{query}"
        return normalized
    except Exception:
        return url


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: Full URL
        
    Returns:
        Domain name
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except Exception:
        return ""


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False


def is_internal_url(url: str, domain: str) -> bool:
    """
    Check if URL belongs to the target domain.
    
    Args:
        url: URL to check
        domain: Target domain
        
    Returns:
        True if internal, False otherwise
    """
    try:
        url_domain = extract_domain(url)
        target_domain = extract_domain(domain if domain.startswith('http') else f'https://{domain}')
        return url_domain == target_domain or url_domain.endswith(f'.{target_domain}')
    except Exception:
        return False


def extract_regex_matches(text: str, patterns: List[str]) -> Set[str]:
    """
    Extract matches from text using multiple regex patterns.
    
    Args:
        text: Text to search
        patterns: List of regex patterns
        
    Returns:
        Set of unique matches
    """
    matches = set()
    for pattern in patterns:
        try:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches.update(found)
        except Exception:
            continue
    return matches


def clean_url(url: str) -> str:
    """
    Clean URL for storage/display.
    
    Args:
        url: URL to clean
        
    Returns:
        Cleaned URL
    """
    return url.strip().lower() if url else ""


def get_status_tag(status_code: int) -> str:
    """
    Get human-readable status tag.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        Status tag like [200], [404], etc.
    """
    return f"[{status_code}]" if status_code else "[UNKNOWN]"


def deduplicate_urls(urls: List[str]) -> List[str]:
    """
    Remove duplicate URLs while preserving order.
    
    Args:
        urls: List of URLs
        
    Returns:
        List with duplicates removed
    """
    seen = set()
    result = []
    for url in urls:
        clean = clean_url(url)
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def get_wordlist() -> List[str]:
    """
    Get default wordlist for brute force.
    
    Returns:
        List of common path words
    """
    return [
        'admin', 'login', 'dashboard', 'api', 'test', 'backup', 'dev', 'old',
        'uploads', 'download', 'files', 'images', 'assets', 'js', 'css',
        'config', 'settings', 'user', 'users', 'account', 'accounts',
        'profile', 'search', 'index', 'home', 'about', 'contact', 'help',
        'support', 'blog', 'news', 'products', 'services', 'docs',
        'documentation', 'api/v1', 'api/v2', 'auth', 'register', 'logout',
        'password', 'reset', 'forgot', 'verify', 'confirm', 'activate',
        'sitemap', 'robots', 'favicon', '.git', '.env', '.htaccess',
        'web.config', 'package.json', 'wp-admin', 'wp-login', 'admin.php',
        'xmlrpc.php', 'shell', 'cmd', 'execute', 'upload', 'download',
        'file', 'folder', 'directory', 'list', 'browse', 'view'
    ]
