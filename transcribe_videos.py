#!/usr/bin/env python3
"""
YTScriptify CLI Tool - Transcribe YouTube videos and save to files

Usage:
    python3 transcribe_videos.py                 # Interactive mode
    python3 transcribe_videos.py <url1> <url2>  # Batch mode
"""

import sys
import os
import requests
import time
from datetime import datetime
from client import YTScriptifyClient


def save_transcripts(job_result: dict, output_dir: str = './transcripts') -> list:
    """
    Save transcripts from completed job to .txt files.
    
    Args:
        job_result: Job result dict from API
        output_dir: Directory to save files (created if doesn't exist)
    
    Returns:
        List of saved file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    saved_files = []
    
    print(f"💾 Saving transcripts...\n")
    
    for transcript_data in job_result['transcripts']:
        url = transcript_data['url']
        video_id = transcript_data['video_id']
        status = transcript_data['status']
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{video_id}_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        # Write transcript file
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
    """Main CLI entry point"""
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
        print("   or: python transcribe_videos.py  (interactive mode)")
        return
    
    print(f"\n📝 {len(urls)} URL(s) to transcribe:")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    
    # Ask for output directory
    output_dir = input(f"\nOutput directory (default: ./transcripts): ").strip() or './transcripts'
    
    # Create client and transcribe
    print(f"\n🎬 Transcribing {len(urls)} video(s)...\n")
    
    try:
        client = YTScriptifyClient()
        job_id = client.submit_job(urls)
        print(f"✓ Job submitted: {job_id}\n")
        
        print(f"⏳ Waiting for transcription...")
        job_result = client.wait_for_completion(job_id, poll_interval=3, max_wait=3600)
        print(f"\n✓ Job finished!\n")
        
        # Save to files
        saved_files = save_transcripts(job_result, output_dir)
        
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
    
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API at http://localhost:5000")
        print("Make sure the Flask app is running!")
        print("Run: python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
