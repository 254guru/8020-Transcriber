from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from uuid import uuid4
import logging
from functools import wraps
from datetime import datetime
from urllib.parse import urlparse
from config import CONFIG
from models import db, Job, Transcript
from celery_app import celery, transcribe_videos

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(CONFIG)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS for all routes
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[CONFIG.REQUEST_LIMIT]
    )
    
    with app.app_context():
        db.create_all()
    
    return app, limiter

app, limiter = create_app()

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != CONFIG.API_KEY:
            logger.warning(f"Unauthorized API key attempt from {get_remote_address()}")
            abort(401, 'Invalid API key')
        return f(*args, **kwargs)
    return decorated_function

def validate_callback_url(url):
    """
    Validates that callback_url is a proper HTTP(S) URL.
    Returns True if valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'service': 'YTScriptify API',
        'version': '2.0',
        'status': 'operational'
    }), 200

@app.route('/transcribe', methods=['POST'])
@limiter.limit("10/minute")
@require_api_key
def transcribe():
    """
    Submit a transcription job.
    
    Expected JSON:
    {
        "youtube_urls": ["https://youtu.be/..."],
        "callback_url": "https://your-callback-endpoint.com"
    }
    """
    try:
        data = request.json
        youtube_urls = data.get('youtube_urls', [])
        callback_url = data.get('callback_url')
        
        # Validation
        if not youtube_urls:
            logger.warning("Missing youtube_urls parameter")
            abort(400, 'Missing required parameter: youtube_urls')
        
        if not isinstance(youtube_urls, list):
            logger.warning("youtube_urls is not a list")
            abort(400, 'youtube_urls must be a list')
        
        if len(youtube_urls) > CONFIG.MAX_URLS_PER_JOB:
            logger.warning(f"Too many URLs: {len(youtube_urls)} > {CONFIG.MAX_URLS_PER_JOB}")
            abort(400, f'Maximum {CONFIG.MAX_URLS_PER_JOB} URLs per job')
        
        if not callback_url:
            logger.warning("Missing callback_url parameter")
            abort(400, 'Missing required parameter: callback_url')
        
        if not validate_callback_url(callback_url):
            logger.warning(f"Invalid callback_url format: {callback_url}")
            abort(400, 'callback_url must be a valid HTTP(S) URL')
        
        # Create job record
        job_id = str(uuid4())
        job = Job(id=job_id, status='pending', callback_url=callback_url)
        db.session.add(job)
        db.session.commit()
        
        logger.info(f"Created job {job_id} with {len(youtube_urls)} URLs")
        
        # Queue background task
        transcribe_videos.delay(job_id, youtube_urls, callback_url)
        
        return jsonify({
            'job_id': job_id,
            'status': 'pending',
            'message': 'Transcription job queued. Check status using the job_id.'
        }), 202  # Accepted
    
    except Exception as e:
        logger.error(f"Error in transcribe endpoint: {str(e)}")
        abort(500, str(e))

@app.route('/job_status/<job_id>', methods=['GET'])
@limiter.limit("30/minute")
@require_api_key
def job_status(job_id):
    """
    Retrieve the status of a transcription job.
    """
    try:
        job = Job.query.get(job_id)
        
        if not job:
            logger.warning(f"Job not found: {job_id}")
            abort(404, 'Job ID not found')
        
        logger.info(f"Status check for job {job_id}: {job.status}")
        return jsonify(job.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Error in job_status endpoint: {str(e)}")
        abort(500, str(e))

@app.route('/jobs', methods=['GET'])
@limiter.limit("10/minute")
@require_api_key
def list_jobs():
    """
    List all jobs (with pagination support).
    Query parameters: page (default 1), per_page (default 10)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        jobs_paginated = Job.query.paginate(page=page, per_page=per_page)
        
        logger.info(f"Listed jobs: page {page}, per_page {per_page}")
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs_paginated.items],
            'total': jobs_paginated.total,
            'pages': jobs_paginated.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        logger.error(f"Error in list_jobs endpoint: {str(e)}")
        abort(500, str(e))

@app.route('/job_status/<job_id>', methods=['DELETE'])
@limiter.limit("5/minute")
@require_api_key
def cancel_job(job_id):
    """
    Cancel a transcription job (only if still pending or processing).
    """
    try:
        job = Job.query.get(job_id)
        
        if not job:
            logger.warning(f"Job not found for deletion: {job_id}")
            abort(404, 'Job ID not found')
        
        if job.status not in ['pending', 'processing']:
            logger.warning(f"Cannot cancel job {job_id} with status {job.status}")
            abort(400, f'Cannot cancel job with status: {job.status}')
        
        job.status = 'cancelled'
        job.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Cancelled job {job_id}")
        
        return jsonify({
            'message': 'Job cancelled successfully',
            'job_id': job_id,
            'status': 'cancelled'
        }), 200
    
    except Exception as e:
        logger.error(f"Error cancelling job: {str(e)}")
        abort(500, str(e))

@app.errorhandler(400)
def bad_request(e):
    """Handle 400 errors"""
    return jsonify({'error': str(e.description)}), 400

@app.errorhandler(401)
def unauthorized(e):
    """Handle 401 errors"""
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': str(e.description)}), 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit errors"""
    return jsonify({'error': 'Rate limit exceeded'}), 429

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=CONFIG.DEBUG)

