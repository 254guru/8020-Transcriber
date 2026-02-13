#!/usr/bin/env python3
"""
YTScriptify API Examples - Shows how to use the API in your code

See client.py for the YTScriptifyClient class documentation.
For transcribing videos and saving files, use: transcribe_videos.py
"""

import requests
from client import YTScriptifyClient


def example_basic_usage():
    """Example 1: Basic usage with polling"""
    print("=" * 70)
    print("Example 1: Basic Usage - Submit Job and Poll for Results")
    print("=" * 70)
    
    client = YTScriptifyClient('http://localhost:5000', 'dev-api-key-12345')
    
    urls = ['https://youtu.be/jNQXAC9IVRw']
    
    print(f"\n📝 Submitting job for {len(urls)} video(s)...")
    job_id = client.submit_job(urls)
    print(f"✓ Job ID: {job_id}\n")
    
    print(f"⏳ Polling for completion...")
    result = client.wait_for_completion(job_id, poll_interval=2, max_wait=60)
    
    if result['status'] == 'completed':
        print(f"\n✓ Job completed!")
        for transcript in result['transcripts']:
            print(f"\nVideo: {transcript['url']}")
            print(f"Status: {transcript['status']}")
            if transcript['status'] == 'completed':
                data = transcript['transcript']
                text = ''.join([item['text'] for item in data]) if isinstance(data, list) else str(data)
                print(f"Preview: {text[:150]}...")
    else:
        print(f"\n✗ Job failed: {result.get('error_message')}")
    
    print()


def example_batch_processing():
    """Example 2: Batch processing multiple URLs"""
    print("=" * 70)
    print("Example 2: Batch Processing - Multiple URLs at Once")
    print("=" * 70)
    
    client = YTScriptifyClient('http://localhost:5000', 'dev-api-key-12345')
    
    urls = [
        'https://youtu.be/jNQXAC9IVRw',
        'https://youtu.be/dQw4w9WgXcQ',
        'https://youtu.be/9bZkp7q19f0'
    ]
    
    print(f"\n📝 Submitting batch job for {len(urls)} videos...")
    job_id = client.submit_job(urls)
    print(f"✓ Job ID: {job_id}\n")
    
    print(f"⏳ Polling for completion...")
    result = client.wait_for_completion(job_id, poll_interval=3, max_wait=300)
    
    completed = sum(1 for t in result['transcripts'] if t['status'] == 'completed')
    failed = sum(1 for t in result['transcripts'] if t['status'] == 'failed')
    
    print(f"\n✓ Batch Results:")
    print(f"  Completed: {completed}/{len(urls)}")
    print(f"  Failed: {failed}/{len(urls)}\n")
    
    for i, transcript in enumerate(result['transcripts'], 1):
        status_icon = "✓" if transcript['status'] == 'completed' else "✗"
        print(f"  {status_icon} [{i}] {transcript['url']}")
        if transcript['error_message']:
            print(f"       Error: {transcript['error_message']}")
    
    print()


def example_list_jobs():
    """Example 3: List and inspect jobs"""
    print("=" * 70)
    print("Example 3: List All Jobs")
    print("=" * 70)
    
    client = YTScriptifyClient('http://localhost:5000', 'dev-api-key-12345')
    
    print(f"\n📋 Fetching job list...")
    jobs_data = client.list_jobs(page=1, per_page=5)
    
    print(f"\nTotal jobs: {jobs_data['total']}")
    print(f"Pages: {jobs_data['pages']}")
    print(f"\nRecent jobs:")
    
    for job in jobs_data['jobs']:
        print(f"\n  ID: {job['id'][:8]}...")
        print(f"  Status: {job['status']}")
        print(f"  Created: {job['created_at']}")
        print(f"  Transcripts: {len(job['transcripts'])}")
    
    print()


def example_error_handling():
    """Example 4: Handling errors gracefully"""
    print("=" * 70)
    print("Example 4: Error Handling")
    print("=" * 70)
    
    client = YTScriptifyClient('http://localhost:5000', 'dev-api-key-12345')
    
    print(f"\n📝 Submitting job with invalid URL to show error handling...")
    
    try:
        urls = ['not-a-youtube-url']
        job_id = client.submit_job(urls)
        print(f"✓ Job ID: {job_id}\n")
        
        print(f"⏳ Polling for completion...")
        result = client.wait_for_completion(job_id, max_wait=30)
        
        transcript = result['transcripts'][0]
        print(f"\n✓ Job completed (with error):")
        print(f"  URL: {transcript['url']}")
        print(f"  Status: {transcript['status']}")
        print(f"  Error: {transcript['error_message']}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_callback_url():
    """Example 5: Using callback URL for notifications"""
    print("=" * 70)
    print("Example 5: Callback URL (Webhook Notifications)")
    print("=" * 70)
    
    print("""
Callbacks allow the API to notify your application when a job completes.

When a job finishes (successfully or with errors), the API sends a POST
request to your callback_url with the complete job result.

Example:
    client = YTScriptifyClient(...)
    job_id = client.submit_job(
        urls,
        callback_url='https://your-app.com/webhooks/transcription'
    )

Your webhook should handle POST requests with this body:
    {
        "id": "job-uuid",
        "status": "completed",
        "transcripts": [...],
        "created_at": "2026-02-13T...",
        "updated_at": "2026-02-13T..."
    }
""")


def main():
    """Main menu"""
    import sys
    
    print("\n")
    print("YTScriptify API Client - Examples")
    print("=" * 70)
    print("Choose an example to run:\n")
    print("1. Basic Usage (single video)")
    print("2. Batch Processing (multiple videos)")
    print("3. List All Jobs")
    print("4. Error Handling")
    print("5. Callback URL (webhook notifications)")
    print("=" * 70)
    
    choice = input("\nSelect example (1-5): ").strip()
    
    try:
        if choice == '1':
            example_basic_usage()
        elif choice == '2':
            example_batch_processing()
        elif choice == '3':
            example_list_jobs()
        elif choice == '4':
            example_error_handling()
        elif choice == '5':
            example_callback_url()
        else:
            print("Invalid choice!")
            sys.exit(1)
        
        print("✓ Example completed!\n")
    
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API at http://localhost:5000")
        print("  Make sure the Flask app is running: python app.py")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
