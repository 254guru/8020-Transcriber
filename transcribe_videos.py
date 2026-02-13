#!/usr/bin/env python3
"""
Simple YouTube Transcriber - One command to transcribe and save
Usage: python transcribe_videos.py <url1> <url2> ... <urlN>
Or: python transcribe_videos.py  (interactive mode)
"""

import sys
import os
import requests
import time
import json
from datetime import datetime


class SimpleTranscriber:
    def __init__(self, base_url='http://localhost:5000', api_key='dev-api-key-12345'):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def transcribe(self, youtube_urls, output_dir='./transcripts', callback_url='http://localhost:8000/webhook'):
        """
        Transcribe YouTube videos and save to files
        """
        # Submit job
        print(f"\n🎬 Transcribing {len(youtube_urls)} video(s)...\n")
        
        try:
            response = self.session.post(
                f'{self.base_url}/transcribe',
                json={
                    'youtube_urls': youtube_urls,
                    'callback_url': callback_url
                }
            )
            response.raise_for_status()
            job_id = response.json()['job_id']
            print(f"✓ Job submitted: {job_id}\n")
        except Exception as e:
            print(f"✗ Failed to submit job: {e}")
            return None
        
        # Poll for completion
        print(f"⏳ Waiting for transcription...")
        max_wait = 3600  # 1 hour
        poll_interval = 3
        elapsed = 0
        
        while elapsed < max_wait:
            try:
                response = self.session.get(f'{self.base_url}/job_status/{job_id}')
                response.raise_for_status()
                job = response.json()
                status = job['status']
                
                print(f"   Status: {status}")
                
                if status in ['completed', 'failed', 'cancelled']:
                    print(f"\n✓ Job finished!\n")
                    return job
                
                time.sleep(poll_interval)
                elapsed += poll_interval
                
            except Exception as e:
                print(f"✗ Error checking status: {e}")
                return None
        
        print(f"\n✗ Job timed out after {max_wait} seconds")
        return None
    
    def save_transcripts(self, job_result, output_dir='./transcripts'):
        """Save transcripts to .txt files"""
        os.makedirs(output_dir, exist_ok=True)
        saved_files = []
        
        print(f"💾 Saving transcripts...\n")
        
        for transcript_data in job_result['transcripts']:
            url = transcript_data['url']
            video_id = transcript_data['video_id']
            status = transcript_data['status']
            
            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{video_id}_{timestamp}.txt"
            filepath = os.path.join(output_dir, filename)
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"YouTube Video Transcript\n")
                f.write(f"{'=' * 70}\n\n")
                f.write(f"URL: {url}\n")
                f.write(f"Video ID: {video_id}\n")
                f.write(f"Status: {status}\n")
                f.write(f"Transcribed: {transcript_data['created_at']}\n")
                
                if status == 'completed':
                    f.write(f"\n{'=' * 70}\n")
                    f.write(f"TRANSCRIPT\n")
                    f.write(f"{'=' * 70}\n\n")
                    
                    transcript = transcript_data['transcript']
                    if isinstance(transcript, list):
                        for item in transcript:
                            f.write(item['text'])
                            if not item['text'].endswith(' '):
                                f.write(' ')
                    else:
                        f.write(str(transcript))
                else:
                    f.write(f"\nError: {transcript_data.get('error_message', 'Unknown error')}\n")
            
            saved_files.append(filepath)
            print(f"  ✓ {os.path.basename(filepath)}")
        
        return saved_files


def main():
    # Get URLs from command line or ask interactively
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        print("\n" + "=" * 70)
        print("🎬 YouTube Transcriber - Interactive Mode")
        print("=" * 70)
        print("\nEnter YouTube URLs (one per line, empty line to finish):\n")
        
        urls = []
        counter = 1
        while True:
            url = input(f"URL {counter}: ").strip()
            if not url:
                if urls:
                    break
                else:
                    print("Please enter at least one URL!")
                    continue
            urls.append(url)
            counter += 1
    
    if not urls:
        print("No URLs provided!")
        print("Usage: python transcribe_videos.py <url1> <url2> ...")
        return
    
    print(f"\n📝 {len(urls)} URL(s) to transcribe:")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    
    # Ask for output directory
    output_dir = input(f"\nOutput directory (default: ./transcripts): ").strip() or './transcripts'
    
    # Transcribe
    transcriber = SimpleTranscriber()
    job_result = transcriber.transcribe(urls, output_dir)
    
    if not job_result:
        print("\n✗ Transcription failed!")
        return
    
    # Save
    saved_files = transcriber.save_transcripts(job_result, output_dir)
    
    # Summary
    print(f"\n" + "=" * 70)
    print(f"✅ COMPLETE!")
    print(f"=" * 70)
    print(f"Total videos: {len(urls)}")
    completed = sum(1 for t in job_result['transcripts'] if t['status'] == 'completed')
    failed = sum(1 for t in job_result['transcripts'] if t['status'] == 'failed')
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print(f"\n⚠️  Some videos failed to transcribe.")
        print(f"    This usually means the video has no captions enabled.")
        print(f"    Try videos from TED Talks, Khan Academy, or news channels.")
        print(f"    Run: python3 test_videos.py  (to see sample videos with captions)")
    
    print(f"\n📂 Files saved to: {os.path.abspath(output_dir)}\n")
    
    # Show file list
    for file in saved_files:
        size = os.path.getsize(file) / 1024  # KB
        print(f"   • {os.path.basename(file)} ({size:.1f} KB)")
    
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API at http://localhost:5000")
        print("Make sure the Flask app is running!")
        print("Run: python app.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")
