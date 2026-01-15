#!/usr/bin/env python3
"""Test script to verify URL enumeration tool functionality."""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all modules can be imported."""
    logger.info("Testing imports...")
    try:
        from core.utils import normalize_url, extract_domain, is_valid_url
        from core.validator import URLValidator
        from core.js_parser import JSParser
        from core.wayback import WaybackMachine
        from core.bruteforce import BruteForcer
        from core.crawler import LiveCrawler
        from core.main_enum import URLEnumerator
        logger.info("✓ All imports successful")
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_utils():
    """Test utility functions."""
    logger.info("\nTesting utils module...")
    try:
        from core.utils import (
            normalize_url, extract_domain, is_valid_url,
            is_internal_url, clean_url, deduplicate_urls
        )
        
        # Test normalize_url
        assert normalize_url("https://example.com") == "https://example.com/"
        logger.info("  ✓ normalize_url")
        
        # Test extract_domain
        assert extract_domain("https://example.com") == "example.com"
        logger.info("  ✓ extract_domain")
        
        # Test is_valid_url
        assert is_valid_url("https://example.com") == True
        assert is_valid_url("invalid") == False
        logger.info("  ✓ is_valid_url")
        
        # Test is_internal_url
        assert is_internal_url("https://example.com/path", "example.com") == True
        logger.info("  ✓ is_internal_url")
        
        # Test deduplicate_urls
        urls = ["http://example.com", "http://example.com", "http://test.com"]
        dedup = deduplicate_urls(urls)
        assert len(dedup) == 2
        logger.info("  ✓ deduplicate_urls")
        
        logger.info("✓ Utils tests passed")
        return True
    except AssertionError as e:
        logger.error(f"✗ Assertion failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Utils test failed: {e}")
        return False


def test_js_parser():
    """Test JavaScript parser."""
    logger.info("\nTesting JSParser...")
    try:
        from core.js_parser import JSParser
        
        parser = JSParser()
        
        # Test endpoint extraction
        js_code = """
        fetch('/api/users')
        axios.get('/api/posts')
        XMLHttpRequest().open('GET', '/admin/panel')
        """
        
        endpoints = parser.extract_endpoints(js_code)
        assert '/api/users' in endpoints
        assert '/api/posts' in endpoints
        assert '/admin/panel' in endpoints
        
        logger.info("  ✓ Endpoint extraction")
        logger.info("✓ JSParser tests passed")
        return True
    except Exception as e:
        logger.error(f"✗ JSParser test failed: {e}")
        return False


def test_bruteforcer():
    """Test brute forcer."""
    logger.info("\nTesting BruteForcer...")
    try:
        from core.bruteforce import BruteForcer
        
        bf = BruteForcer()
        paths = bf.generate_paths()
        
        assert len(paths) > 0
        assert '/admin' in paths
        assert '/login' in paths
        
        urls = bf.generate_urls("example.com")
        assert len(urls) > 0
        assert any('example.com' in url for url in urls)
        
        logger.info("  ✓ Path generation")
        logger.info("  ✓ URL generation")
        logger.info("✓ BruteForcer tests passed")
        return True
    except Exception as e:
        logger.error(f"✗ BruteForcer test failed: {e}")
        return False


def test_cli():
    """Test CLI module."""
    logger.info("\nTesting CLI...")
    try:
        from cli import create_parser
        
        parser = create_parser()
        
        # Test valid arguments
        args = parser.parse_args(['-d', 'example.com'])
        assert args.domain == 'example.com'
        assert args.depth == 3
        assert args.threads == 50
        
        logger.info("  ✓ Argument parsing")
        logger.info("✓ CLI tests passed")
        return True
    except Exception as e:
        logger.error(f"✗ CLI test failed: {e}")
        return False


def test_structure():
    """Test project file structure."""
    logger.info("\nTesting project structure...")
    try:
        required_files = [
            'main.py',
            'cli.py',
            'requirements.txt',
            'README.md',
            'QUICKSTART.md',
            'core/__init__.py',
            'core/utils.py',
            'core/validator.py',
            'core/js_parser.py',
            'core/wayback.py',
            'core/bruteforce.py',
            'core/crawler.py',
            'core/main_enum.py',
        ]
        
        base_path = Path(__file__).parent
        
        for file in required_files:
            file_path = base_path / file
            if file_path.exists():
                logger.info(f"  ✓ {file}")
            else:
                logger.error(f"  ✗ {file} (missing)")
                return False
        
        logger.info("✓ Project structure verified")
        return True
    except Exception as e:
        logger.error(f"✗ Structure test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("=" * 70)
    logger.info("URL Enumeration Tool - Verification Tests")
    logger.info("=" * 70)
    
    tests = [
        ("Project Structure", test_structure),
        ("Imports", test_imports),
        ("Utils Module", test_utils),
        ("JS Parser", test_js_parser),
        ("Brute Forcer", test_bruteforcer),
        ("CLI Module", test_cli),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"✗ {name} failed: {e}")
            results.append((name, False))
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")
    
    logger.info("=" * 70)
    logger.info(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n✓ All tests passed! Tool is ready to use.")
        logger.info("\nRun: python main.py -d example.com")
        return 0
    else:
        logger.error(f"\n✗ {total - passed} test(s) failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
