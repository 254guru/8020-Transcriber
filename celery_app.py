from celery import Celery
from config import CONFIG
import logging
import sys
import os
import re
import requests
from datetime import datetime

# Add current directory to path so imports work from worker
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Celery
celery = Celery(__name__)
celery.conf.broker_url = CONFIG.CELERY_BROKER_URL
celery.conf.result_backend = CONFIG.CELERY_RESULT_BACKEND
celery.conf.task_serializer = 'json'
celery.conf.accept_content = ['json']
celery.conf.result_serializer = 'json'
celery.conf.timezone = 'UTC'

logger = logging.getLogger(__name__)


def extract_video_id(url):
    """
    Extracts the YouTube video ID from various URL formats.
    """
    pattern = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


@celery.task(bind=True, max_retries=3)
def transcribe_videos(self, job_id, urls, callback_url):
    """
    Background task to transcribe multiple YouTube videos
    """
    from models import db, Job, Transcript
    from youtube_transcript_api import YouTubeTranscriptApi
    from app import create_app
    
    # Create app context for database access
    app, _ = create_app()  # Unpack tuple (app, limiter)
    
    with app.app_context():
        try:
            job = Job.query.get(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return
            
            # Update job status to processing
            job.status = 'processing'
            db.session.commit()
            
            logger.info(f"Starting transcription for job {job_id} with {len(urls)} URLs")
            
            # Process each URL
            for url in urls:
                video_id = extract_video_id(url)
                
                # Create transcript record
                transcript_record = Transcript(job_id=job_id, url=url, video_id=video_id)
                db.session.add(transcript_record)
                db.session.commit()
                
                if not video_id:
                    transcript_record.status = 'failed'
                    transcript_record.error_message = 'Invalid YouTube URL'
                    db.session.commit()
                    logger.warning(f"Invalid URL for job {job_id}: {url}")
                    continue
                
                try:
                    # Fetch transcript
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    transcript_record.set_transcript(transcript)
                    transcript_record.status = 'completed'
                    db.session.commit()
                    logger.info(f"Successfully transcribed {video_id} for job {job_id}")
                    
                except Exception as e:
                    error_str = str(e)
                    # Check if it's a "no captions" error
                    if "no element found" in error_str.lower() or "not available" in error_str.lower():
                        transcript_record.error_message = "Video has no captions available (try videos from TED Talks, Khan Academy, or news channels)"
                    else:
                        transcript_record.error_message = error_str
                    transcript_record.status = 'failed'
                    db.session.commit()
                    logger.error(f"Failed to transcribe {video_id}: {error_str}")
            
            # Update job status to completed
            job.status = 'completed'
            job.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Send callback notification with results
            if callback_url:
                try:
                    payload = {
                        'job_id': job_id,
                        'status': 'completed',
                        'transcripts': [t.to_dict() for t in job.transcripts]
                    }
                    response = requests.post(callback_url, json=payload, timeout=10)
                    logger.info(f"Callback sent for job {job_id}: {response.status_code}")
                except Exception as e:
                    logger.error(f"Failed to send callback for job {job_id}: {str(e)}")
            
            logger.info(f"Completed transcription for job {job_id}")
            
        except Exception as exc:
            job = Job.query.get(job_id)
            job.status = 'failed'
            job.error_message = str(exc)
            db.session.commit()
            logger.error(f"Task failed for job {job_id}: {str(exc)}")
            
            # Retry with exponential backoff
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
