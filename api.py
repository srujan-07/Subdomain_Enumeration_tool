#!/usr/bin/env python3
"""REST API server for autonomous web QA inspection."""

import asyncio
import json
import logging
import uuid
from threading import Thread
from typing import Dict, Any

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sock import Sock

from core.main_enum import URLEnumerator
from qa_engine.core import QAOrchestrator, event_bus, EventType
from qa_engine.hygiene_transformer import (
    qa_results_to_hygiene_pages,
    qa_results_to_summary,
    qa_results_to_worst_pages,
)
from qa_engine.streaming import setup_websocket, ws_manager

app = Flask(__name__)
CORS(app)
sock = Sock(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory scan store for demo; swap with DB/queue in production
SCAN_STORE: Dict[str, Dict[str, Any]] = {}

# Setup WebSocket
setup_websocket(app, sock)


def _run_scan_job(scan_id: str, url: str, depth: int, mode: str,
                  wayback: bool, bruteforce: bool, validate_ssl: bool):
    """Execute enumeration + QA testing in a background thread and store results."""
    try:
        logger.info(f"[scan {scan_id}] starting enumeration for {url}")
        
        # Phase 1: URL Enumeration (existing)
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
            only_alive=validate_ssl
        )

        enum_results = enumerator.enumerate(techniques=techniques)
        SCAN_STORE[scan_id]['enum_results'] = enum_results

        logger.info(f"[scan {scan_id}] enumeration complete: {enum_results['summary']['total_urls']} URLs found")
        
        # Phase 2: QA Analysis (new)
        if mode in ('full', 'qa'):
            logger.info(f"[scan {scan_id}] starting QA analysis")
            
            # Run QA orchestrator in async context
            orchestrator = QAOrchestrator(
                base_url=url,
                max_pages=50,
                http_timeout=10,
                browser_timeout=15,
                crawler_concurrency=10,
                validator_concurrency=20,
                browser_concurrency=5,
                headless=True,
            )
            
            qa_results = asyncio.run(orchestrator.run(scan_id))
            SCAN_STORE[scan_id]['qa_results'] = qa_results
            
            # Transform for frontend
            hygiene_pages = qa_results_to_hygiene_pages(qa_results)
            SCAN_STORE[scan_id]['hygiene_pages'] = hygiene_pages
            
            logger.info(f"[scan {scan_id}] QA analysis complete: {len(hygiene_pages)} pages analyzed")
        else:
            # If not running QA, convert enum results to basic hygiene format
            SCAN_STORE[scan_id]['hygiene_pages'] = _enum_results_to_hygiene(enum_results)

        SCAN_STORE[scan_id]['status'] = 'completed'
        logger.info(f"[scan {scan_id}] scan complete")

    except Exception as exc:
        logger.exception(f"[scan {scan_id}] failed: {exc}")
        SCAN_STORE[scan_id]['status'] = 'failed'
        SCAN_STORE[scan_id]['error'] = str(exc)


def _enum_results_to_hygiene(results: Dict[str, Any]):
    """Convert enumeration results to hygiene format (basic fallback)."""
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
    """Start a URL enumeration and/or QA inspection scan.
    
    Request body:
    {
        "url": "https://example.com",
        "depth": 2,
        "mode": "full|crawl|qa",  # full=both, crawl=enum only, qa=qa only
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
        mode = data.get('mode', 'full')
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

        logger.info(f"Starting scan {scan_id} for {url} (mode={mode})")

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
            response['hygiene_pages'] = scan.get('hygiene_pages', [])
            
            # Include QA results if available
            if 'qa_results' in scan:
                qa = scan['qa_results']
                response['summary'] = qa_results_to_summary(qa)
                response['worst_pages'] = qa_results_to_worst_pages(qa, limit=5)
            
            # Include enumeration results if available
            if 'enum_results' in scan:
                response['enum_results'] = scan['enum_results']
            
            response['progress'] = 100
        elif scan['status'] == 'failed':
            response['error'] = scan.get('error', 'Unknown error')
        else:
            response['progress'] = 10

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
    """Provide hygiene analytics from the latest completed scan."""
    try:
        _, scan_data = _latest_completed_scan()
        if not scan_data:
            return jsonify([]), 200
        
        # Return hygiene pages from the scan
        return jsonify(scan_data.get('hygiene_pages', [])), 200
    except Exception as e:
        logger.error(f"Error getting hygiene data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan/<scan_id>/events', methods=['GET'])
def get_scan_events(scan_id: str):
    """Get event history for a scan (REST polling alternative to WebSocket)."""
    try:
        events = event_bus.get_history(scan_id)
        return jsonify({
            'scan_id': scan_id,
            'events': [e.to_dict() for e in events]
        }), 200
    except Exception as e:
        logger.error(f"Error getting scan events: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
