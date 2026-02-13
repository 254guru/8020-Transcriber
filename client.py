#!/usr/bin/env python3
"""
YTScriptify API Client - Shared client for all tools

This module provides a reusable client for the YTScriptify REST API.
Used by transcribe_videos.py and example_client.py to avoid code duplication.
"""

import requests
import time
from typing import Optional


class YTScriptifyClient:
    """
    REST API client for YTScriptify.
    
    Handles authentication, job submission, status polling, and job management.
    """
    
    def __init__(self, base_url: str = 'http://localhost:5000', 
                 api_key: str = 'dev-api-key-12345'):
        """
        Initialize the API client.
        
        Args:
            base_url: API server URL (default: http://localhost:5000)
            api_key: API key for authentication (default: dev-api-key-12345)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def submit_job(self, youtube_urls: list, callback_url: Optional[str] = None) -> str:
        """
        Submit a transcription job.
        
        Args:
            youtube_urls: List of YouTube URLs to transcribe
            callback_url: Optional webhook URL for completion notification
        
        Returns:
            Job ID (string UUID)
        
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        payload = {'youtube_urls': youtube_urls}
        if callback_url:
            payload['callback_url'] = callback_url
        
        response = self.session.post(
            f'{self.base_url}/transcribe',
            json=payload
        )
        response.raise_for_status()
        return response.json()['job_id']
    
    def get_status(self, job_id: str) -> dict:
        """
        Get the current status of a job.
        
        Args:
            job_id: Job ID to check
        
        Returns:
            Job data including status, transcripts, and metadata
        
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        response = self.session.get(f'{self.base_url}/job_status/{job_id}')
        response.raise_for_status()
        return response.json()
    
    def list_jobs(self, page: int = 1, per_page: int = 10) -> dict:
        """
        List all jobs with pagination.
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 10, max: 100)
        
        Returns:
            Dictionary with jobs list and pagination info
        
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        response = self.session.get(
            f'{self.base_url}/jobs',
            params={'page': page, 'per_page': per_page}
        )
        response.raise_for_status()
        return response.json()
    
    def cancel_job(self, job_id: str) -> dict:
        """
        Cancel a pending or processing job.
        
        Args:
            job_id: Job ID to cancel
        
        Returns:
            Confirmation response
        
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        response = self.session.delete(f'{self.base_url}/job_status/{job_id}')
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, job_id: str, poll_interval: int = 5, 
                           max_wait: int = 300, verbose: bool = True) -> dict:
        """
        Poll job status until completion, timeout, or failure.
        
        Args:
            job_id: Job ID to monitor
            poll_interval: Seconds between polls (default: 5)
            max_wait: Maximum seconds to wait (default: 300 = 5 minutes)
            verbose: Print status updates (default: True)
        
        Returns:
            Completed job data
        
        Raises:
            TimeoutError: If job doesn't complete within max_wait seconds
            requests.exceptions.RequestException: If API request fails
        """
        elapsed = 0
        while elapsed < max_wait:
            status = self.get_status(job_id)
            
            if verbose:
                print(f"  Status: {status['status']}")
            
            if status['status'] in ['completed', 'failed', 'cancelled']:
                return status
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(
            f"Job {job_id} did not complete within {max_wait} seconds"
        )
