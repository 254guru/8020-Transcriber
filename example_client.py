#!/usr/bin/env python3
"""
Example client for YTScriptify API
Demonstrates how to use the API programmatically
"""

import requests
import time
import json
from typing import Optional
import os
from datetime import datetime

class YTScriptifyClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def submit_job(self, youtube_urls: list, callback_url: str) -> str:
        """Submit a transcription job and return job_id"""
        payload = {
            'youtube_urls': youtube_urls,
            'callback_url': callback_url
        }
        response = self.session.post(f'{self.base_url}/transcribe', json=payload)
        response.raise_for_status()
        return response.json()['job_id']
    
    def get_status(self, job_id: str) -> dict:
        """Get current status of a job"""
        response = self.session.get(f'{self.base_url}/job_status/{job_id}')
        response.raise_for_status()
        return response.json()
    
    def list_jobs(self, page: int = 1, per_page: int = 10) -> dict:
        """List all jobs with pagination"""
        response = self.session.get(
            f'{self.base_url}/jobs',
            params={'page': page, 'per_page': per_page}
        )
        response.raise_for_status()
        return response.json()
    
    def cancel_job(self, job_id: str) -> dict:
        """Cancel a pending job"""
        response = self.session.delete(f'{self.base_url}/job_status/{job_id}')
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, job_id: str, poll_interval: int = 5, max_wait: int = 300) -> dict:
        """
        Poll job status until completion
        
        Args:
            job_id: Job ID to monitor
            poll_interval: Seconds between polls (default 5)
            max_wait: Maximum seconds to wait (default 300 = 5 minutes)
        
        Returns:
            Completed job data
        """
        elapsed = 0
        while elapsed < max_wait:
            status = self.get_status(job_id)
            print(f"Job {job_id} status: {status['status']}")
            
            if status['status'] in ['completed', 'failed', 'cancelled']:
                return status
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(f"Job {job_id} did not complete within {max_wait} seconds")


def save_transcripts_to_file(job_result: dict, output_dir: str = './transcripts') -> list:
    """
    Save transcripts from completed job to .txt files
    
    Args:
        job_result: Job result dict from API
        output_dir: Directory to save files (created if doesn't exist)
    
    Returns:
        List of saved file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    saved_files = []
    
    for transcript_data in job_result['transcripts']:
        url = transcript_data['url']
        video_id = transcript_data['video_id']
        status = transcript_data['status']
        
        # Create filename from video ID and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{video_id}_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"YouTube Video Transcript\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(f"Video URL: {url}\n")
            f.write(f"Video ID: {video_id}\n")
            f.write(f"Status: {status}\n")
            f.write(f"Transcribed: {transcript_data['created_at']}\n")
            
            if status == 'completed':
                f.write(f"\n{'=' * 60}\n")
                f.write(f"TRANSCRIPT\n")
                f.write(f"{'=' * 60}\n\n")
                
                # Get transcript data and format it
                transcript = transcript_data['transcript']
                if isinstance(transcript, list):
                    # Each item has 'text', 'start', 'duration'
                    for item in transcript:
                        f.write(item['text'])
                        if not item['text'].endswith(' '):
                            f.write(' ')
                else:
                    f.write(str(transcript))
            else:
                f.write(f"\nError: {transcript_data.get('error_message', 'Unknown error')}\n")
        
        saved_files.append(filepath)
        print(f"✓ Saved: {filepath}")
    
    return saved_files


def transcribe_and_save(youtube_urls: list, output_dir: str = './transcripts', 
                       base_url: str = 'http://localhost:5000',
                       api_key: str = 'dev-api-key-12345',
                       callback_url: str = 'http://localhost:8000/webhook') -> dict:
    """
    Transcribe YouTube videos and save results to files
    
    Args:
        youtube_urls: List of YouTube URLs to transcribe
        output_dir: Directory to save transcript files
        base_url: API base URL
        api_key: API key for authentication
        callback_url: Callback URL for the API
    
    Returns:
        Job result dictionary with file paths added
    """
    print(f"\n{'=' * 60}")
    print(f"YTScriptify - Transcribe and Save")
    print(f"{'=' * 60}\n")
    
    client = YTScriptifyClient(base_url, api_key)
    
    print(f"📝 Submitting {len(youtube_urls)} video(s) for transcription...")
    
    try:
        job_id = client.submit_job(youtube_urls, callback_url)
        print(f"✓ Job submitted: {job_id}\n")
        
        print(f"⏳ Waiting for transcription to complete...")
        print(f"   (This may take a few minutes depending on video length)\n")
        
        result = client.wait_for_completion(job_id, poll_interval=3, max_wait=3600)
        
        print(f"\n✓ Transcription complete!\n")
        
        # Save to files
        print(f"💾 Saving transcripts to files...\n")
        saved_files = save_transcripts_to_file(result, output_dir)
        
        # Add file paths to result
        result['saved_files'] = saved_files
        
        # Print summary
        completed = sum(1 for t in result['transcripts'] if t['status'] == 'completed')
        failed = sum(1 for t in result['transcripts'] if t['status'] == 'failed')
        
        print(f"\n{'=' * 60}")
        print(f"SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total videos: {len(youtube_urls)}")
        print(f"Completed: {completed}")
        print(f"Failed: {failed}")
        print(f"Output directory: {os.path.abspath(output_dir)}\n")
        
        return result
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


def interactive_transcribe():
    """
    Interactive mode - ask user for YouTube URLs
    """
    print(f"\n{'=' * 60}")
    print(f"🎬 YTScriptify Interactive Transcriber")
    print(f"{'=' * 60}\n")
    
    print("Configuration (press Enter to use defaults):\n")
    
    base_url = input("API URL (default: http://localhost:5000): ").strip() or 'http://localhost:5000'
    api_key = input("API Key (default: dev-api-key-12345): ").strip() or 'dev-api-key-12345'
    output_dir = input("Output directory (default: ./transcripts): ").strip() or './transcripts'
    
    print(f"\n{'=' * 60}\n")
    print(f"✓ Using API at: {base_url}")
    print(f"✓ Output dir: {output_dir}\n")
    print(f"{'=' * 60}\n")
    
    print("Enter YouTube URLs (one per line, empty line to finish):\n")
    urls = []
    while True:
        url = input(f"URL {len(urls) + 1}: ").strip()
        if not url:
            break
        urls.append(url)
    
    if not urls:
        print("No URLs provided!")
        return
    
    try:
        result = transcribe_and_save(
            urls,
            output_dir=output_dir,
            base_url=base_url,
            api_key=api_key
        )
        
        print(f"✓ All done! Transcripts saved to: {os.path.abspath(output_dir)}")
        
    except requests.exceptions.ConnectionError:
        print(f"\n✗ Error: Could not connect to API at {base_url}")
        print(f"  Make sure the Flask app is running!")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_basic_usage():
    """Example 1: Basic usage with polling"""
    print("=" * 60)
    print("Example 1: Basic Usage with Polling")
    print("=" * 60)
    
    client = YTScriptifyClient('http://localhost:5000', 'dev-api-key-12345')
    
    # Submit job
    urls = ['https://www.youtube.com/watch?v=w-WRZVPM-tg']
    job_id = client.submit_job(urls, callback_url='http://localhost:8000/webhook')
    print(f"✓ Job submitted: {job_id}")
    
    # Poll for completion
    result = client.wait_for_completion(job_id, poll_interval=2)
    
    if result['status'] == 'completed':
        print(f"✓ Job completed!")
        for transcript in result['transcripts']:
            print(f"\nVideo: {transcript['url']}")
            print(f"Status: {transcript['status']}")
            if transcript['status'] == 'completed':
                data = transcript['transcript']
                print(f"First 100 chars: {str(data)[:100]}...")
    else:
        print(f"✗ Job failed: {result.get('error_message')}")
    
    print()


def example_batch_processing():
    """Example 2: Batch processing multiple URLs"""
    print("=" * 60)
    print("Example 2: Batch Processing")
    print("=" * 60)
    
    client = YTScriptifyClient('http://localhost:5000', 'dev-api-key-12345')
    
    urls = [
        'https://youtu.be/dQw4w9WgXcQ',
        'https://youtu.be/9bZkp7q19f0',
        'https://youtu.be/kJQP7kiw9Fk'
    ]
    
    job_id = client.submit_job(urls, callback_url='http://localhost:8000/webhook')
    print(f"✓ Batch job submitted: {job_id}")
    print(f"  Processing {len(urls)} videos...")
    
    result = client.wait_for_completion(job_id, poll_interval=3, max_wait=600)
    
    completed = sum(1 for t in result['transcripts'] if t['status'] == 'completed')
    failed = sum(1 for t in result['transcripts'] if t['status'] == 'failed')
    
    print(f"\n✓ Results:")
    print(f"  Completed: {completed}/{len(urls)}")
    print(f"  Failed: {failed}/{len(urls)}")
    
    for i, transcript in enumerate(result['transcripts'], 1):
        print(f"\n  [{i}] {transcript['url']}")
        print(f"      Status: {transcript['status']}")
        if transcript['error_message']:
            print(f"      Error: {transcript['error_message']}")
    
    print()


def example_list_jobs():
    """Example 3: List and monitor jobs"""
    print("=" * 60)
    print("Example 3: List All Jobs")
    print("=" * 60)
    
    client = YTScriptifyClient('http://localhost:5000', 'dev-api-key-12345')
    
    jobs_data = client.list_jobs(page=1, per_page=5)
    
    print(f"Total jobs: {jobs_data['total']}")
    print(f"Pages: {jobs_data['pages']}")
    print(f"\nRecent jobs:")
    
    for job in jobs_data['jobs']:
        print(f"\n  ID: {job['id'][:8]}...")
        print(f"  Status: {job['status']}")
        print(f"  Created: {job['created_at']}")
        print(f"  Transcripts: {len(job['transcripts'])}")
    
    print()


def example_error_handling():
    """Example 4: Error handling"""
    print("=" * 60)
    print("Example 4: Error Handling")
    print("=" * 60)
    
    client = YTScriptifyClient('http://localhost:5000', 'dev-api-key-12345')
    
    # Try invalid URL
    try:
        urls = ['not-a-youtube-url']
        job_id = client.submit_job(urls, callback_url='http://localhost:8000/webhook')
        result = client.wait_for_completion(job_id, max_wait=30)
        
        print(f"✓ Job submitted even with invalid URL: {job_id}")
        print(f"  Status: {result['status']}")
        print(f"  Transcript status: {result['transcripts'][0]['status']}")
        print(f"  Error: {result['transcripts'][0]['error_message']}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


if __name__ == '__main__':
    import sys
    
    print("\n")
    print("YTScriptify Client - Main Menu")
    print("=" * 60)
    print("1. Interactive Mode (enter URLs, save to files)")
    print("2. Run Examples")
    print("=" * 60)
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    try:
        if choice == '1':
            interactive_transcribe()
        else:
            print("\nRunning Examples...")
            print("Make sure the API is running on http://localhost:5000\n")
            
            # Run examples
            example_basic_usage()
            example_batch_processing()
            example_list_jobs()
            example_error_handling()
            
            print("✓ All examples completed!")
    
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to API at http://localhost:5000")
        print("  Make sure the Flask app is running!")
        sys.exit(1)
    
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
