"""CLI interface for URL enumeration tool."""

import argparse
import sys
import logging
from pathlib import Path


def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description='Complete URL/Page Enumeration Tool - Discover all accessible pages of a domain',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s -d example.com
  %(prog)s -d example.com --depth 5 --threads 100
  %(prog)s -d example.com --only-alive --json -o results.json
  %(prog)s -d example.com --silent
        '''
    )
    
    # Required arguments
    parser.add_argument(
        '-d', '--domain',
        required=True,
        help='Target domain (e.g., example.com or https://example.com)'
    )
    
    # Optional flags
    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='Crawl depth for live crawling (default: 3)'
    )
    
    parser.add_argument(
        '--threads',
        type=int,
        default=50,
        help='Number of concurrent threads (default: 50)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=5,
        help='Request timeout in seconds (default: 5)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    parser.add_argument(
        '--txt',
        action='store_true',
        help='Output results in TXT format (one URL per line, default)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path'
    )
    
    parser.add_argument(
        '--silent',
        action='store_true',
        help='Only print URLs, no summary or details'
    )
    
    parser.add_argument(
        '--only-alive',
        action='store_true',
        help='Only return URLs with HTTP 200/3xx status codes'
    )
    
    parser.add_argument(
        '--techniques',
        default='live,js,wayback,bruteforce,robots,sitemap',
        help='Comma-separated list of techniques to use (default: all). Options: live,js,wayback,bruteforce,robots,sitemap'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output (debug logging)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress all logging except URLs'
    )
    
    return parser


def setup_logging(verbose: bool = False, quiet: bool = False):
    """Configure logging."""
    if quiet:
        log_level = logging.ERROR
    elif verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def format_output_txt(urls: list) -> str:
    """Format URLs as plain text."""
    return '\n'.join(urls)


def format_output_json(results: dict) -> str:
    """Format results as JSON."""
    import json
    
    # Convert sets to lists for JSON serialization
    json_results = {
        'urls': results['urls'],
        'summary': results['summary'],
        'details': {}
    }
    
    for url, details in results['url_details'].items():
        json_results['details'][url] = {
            'status': details['status'],
            'status_tag': details['status_tag'],
            'content_length': details['content_length'],
            'alive': details['alive'],
            'sources': details['sources']
        }
    
    return json.dumps(json_results, indent=2)


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose, quiet=args.quiet)
    logger = logging.getLogger(__name__)
    
    # Validate domain
    domain = args.domain.strip()
    if not domain:
        logger.error("Domain cannot be empty")
        sys.exit(1)
    
    # Parse techniques
    techniques = [t.strip() for t in args.techniques.split(',')]
    valid_techniques = ['live', 'js', 'wayback', 'bruteforce', 'robots', 'sitemap']
    techniques = [t for t in techniques if t in valid_techniques]
    
    if not techniques:
        logger.error("No valid techniques specified")
        sys.exit(1)
    
    # Determine output format
    output_format = 'txt'
    if args.json:
        output_format = 'json'
    elif args.txt:
        output_format = 'txt'
    
    try:
        # Import here to avoid issues if dependencies missing
        from core.main_enum import URLEnumerator
        
        logger.info("=" * 70)
        logger.info("URL Enumeration Tool Started")
        logger.info("=" * 70)
        
        # Run enumeration
        enumerator = URLEnumerator(
            domain=domain,
            depth=args.depth,
            timeout=args.timeout,
            threads=args.threads,
            only_alive=args.only_alive
        )
        
        results = enumerator.enumerate(techniques=techniques)
        
        # Format output
        if output_format == 'json':
            output = format_output_json(results)
        else:
            output = format_output_txt(results['urls'])
        
        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            logger.info(f"Results saved to {output_path}")
        else:
            print(output)
        
        # Print summary if not silent
        if not args.silent:
            print("\n" + "=" * 70)
            print("ENUMERATION SUMMARY")
            print("=" * 70)
            print(f"Domain: {domain}")
            print(f"Total URLs Found: {results['summary']['total_urls']}")
            print(f"Alive URLs: {results['summary']['alive_urls']}")
            print(f"Techniques Used: {', '.join(results['summary']['sources_used'])}")
            print("\nURLs by Source:")
            for source, count in results['summary']['sources_summary'].items():
                print(f"  {source}: {count}")
            print("=" * 70)
        
        logger.info("Enumeration completed successfully")
        sys.exit(0)
    
    except KeyboardInterrupt:
        logger.warning("\nEnumeration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == '__main__':
    main()
