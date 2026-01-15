#!/usr/bin/env python3
"""REST API server for the URL enumeration tool."""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import uuid
from threading import Thread
from typing import Dict, Any
from core.main_enum import URLEnumerator

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory scan store for demo; swap with DB/queue in production
SCAN_STORE: Dict[str, Dict[str, Any]] = {}


def _run_scan_job(scan_id: str, url: str, depth: int, mode: str,
                  wayback: bool, bruteforce: bool, validate_ssl: bool):
    """Execute enumeration in a background thread and store results."""
    try:
        logger.info(f"[scan {scan_id}] running enumeration for {url}")
        techniques = ['live', 'js']
        if wayback:
            techniques.append('wayback')
        if bruteforce:
            techniques.append('bruteforce')
        techniques += ['robots', 'sitemap']

        enumerator = URLEnumerator(
            domain=url,
            depth=depth,
            timeout=5,
            threads=50,
            only_alive=validate_ssl  # reuse flag to filter alive URLs only
        )

        results = enumerator.enumerate(techniques=techniques)

        SCAN_STORE[scan_id]['status'] = 'completed'
        SCAN_STORE[scan_id]['results'] = results
        logger.info(f"[scan {scan_id}] completed with {results['summary']['total_urls']} URLs")

    except Exception as exc:  # pragma: no cover - safety net
        logger.exception(f"[scan {scan_id}] failed: {exc}")
        SCAN_STORE[scan_id]['status'] = 'failed'
        SCAN_STORE[scan_id]['error'] = str(exc)


def _latest_completed_scan():
    """Return latest completed scan data, if any."""
    for scan_id, data in reversed(list(SCAN_STORE.items())):
        if data.get('status') == 'completed' and 'results' in data:
            return scan_id, data['results']
    return None, None


def _results_to_hygiene(results: Dict[str, Any]):
    """Map enumeration results into hygiene payload consumed by the UI."""
    pages = []
    details = results.get('url_details', {}) if results else {}
    for url, meta in details.items():
        alive = meta.get('alive', False)
        status = meta.get('status') or 0
        score = 90 if alive else 50
        if status >= 500:
            score = 30
        pages.append({
            'url': url,
            'type': 'page',
            'score': score,
            'issues': [],
        })
    return pages

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'url-enumeration-api'})

@app.route('/api/scan', methods=['POST'])
def start_scan():
    """Start a URL enumeration scan.
    
    Request body:
    {
        "url": "https://example.com",
        "depth": 2,
        "mode": "full",
        "wayback": true,
        "bruteforce": true,
        "validate_ssl": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'Missing required field: url'}), 400
        
        url = data.get('url')
        depth = data.get('depth', 2)
        mode = data.get('mode', 'crawl')
        wayback = data.get('wayback', False)
        bruteforce = data.get('bruteforce', False)
        validate_ssl = data.get('validate_ssl', True)

        scan_id = f"scan_{uuid.uuid4().hex[:8]}"
        SCAN_STORE[scan_id] = {
            'status': 'running',
            'url': url,
            'config': {
                'depth': depth,
                'mode': mode,
                'wayback': wayback,
                'bruteforce': bruteforce,
                'validate_ssl': validate_ssl
            }
        }

        thread = Thread(target=_run_scan_job, args=(scan_id, url, depth, mode, wayback, bruteforce, validate_ssl))
        thread.daemon = True
        thread.start()

        logger.info(f"Starting scan {scan_id} for {url}")

        return jsonify({
            'status': 'started',
            'scan_id': scan_id,
            'url': url,
            'config': SCAN_STORE[scan_id]['config'],
            'message': 'Scan started successfully'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting scan: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<scan_id>', methods=['GET'])
def get_scan_status(scan_id):
    """Get scan status and results."""
    try:
        scan = SCAN_STORE.get(scan_id)
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404

        response = {
            'scan_id': scan_id,
            'status': scan['status'],
            'url': scan['url'],
            'config': scan['config'],
        }

        if scan['status'] == 'completed':
            response['results'] = scan.get('results', {})
            response['progress'] = 100
        elif scan['status'] == 'failed':
            response['error'] = scan.get('error', 'Unknown error')
        else:
            response['progress'] = 10  # basic placeholder; wire to real progress tracker if added

        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting scan status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<scan_id>', methods=['DELETE'])
def cancel_scan(scan_id):
    """Cancel an ongoing scan."""
    try:
        # TODO: Implement cancel functionality
        return jsonify({
            'scan_id': scan_id,
            'status': 'cancelled',
            'message': 'Scan cancelled successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error cancelling scan: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/hygiene', methods=['GET'])
def get_hygiene():
    """Provide hygiene analytics derived from the latest completed scan."""
    try:
        _, results = _latest_completed_scan()
        if not results:
            return jsonify([]), 200
        return jsonify(_results_to_hygiene(results)), 200
    except Exception as e:
        logger.error(f"Error getting hygiene data: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
