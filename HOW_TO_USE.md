# How to Transcribe YouTube Videos

There are **2 easy ways** to transcribe and save YouTube videos:

## Option 1: Simple Command (Recommended) ⭐

**Most straightforward way to use it:**

```bash
# Interactive mode - enter URLs one by one
python3 transcribe_videos.py

# Or pass URLs directly
python3 transcribe_videos.py "https://www.youtube.com/watch?v=..." "https://youtu.be/..."
```

**What happens:**
1. Enter YouTube URLs
2. Choose output directory (default: `./transcripts`)
3. Wait for transcription
4. ✅ Transcript files saved as `.txt`

---

## Option 2: Example Client (Advanced)

```bash
python3 example_client.py
```

**Menu options:**
- **Option 1**: Interactive mode (enter URLs, save to files)
- **Option 2**: Run examples (see API in action)

---

## Output Files

Transcripts are saved to `./transcripts/` by default:

```
transcripts/
├── w-WRZVPM-tg_20260213_143022.txt
├── AxNyNHYSN60_20260213_143150.txt
└── dQw4w9WgXcQ_20260213_143045.txt
```

**File format:**
```
YouTube Video Transcript
==============================================================================

URL: https://www.youtube.com/watch?v=w-WRZVPM-tg
Video ID: w-WRZVPM-tg
Status: completed
Transcribed: 2026-02-13T14:30:22.123456

==============================================================================
TRANSCRIPT
==============================================================================

This is the actual transcript text from the YouTube video...
```

---

## Before You Start

Make sure the API is running:

```bash
# Terminal 1: Start Redis
docker-compose up -d redis

# Terminal 2: Start Celery Worker
celery -A celery_app worker --loglevel=info

# Terminal 3: Start Flask API
python app.py
```

Then in Terminal 4, run the transcriber:
```bash
python3 transcribe_videos.py
```

---

## Examples

### Example 1: Transcribe a Single Video (Interactive)

```bash
$ python3 transcribe_videos.py

🎬 YouTube Transcriber - Interactive Mode
======================================================================

Enter YouTube URLs (one per line, empty line to finish):

URL 1: https://www.youtube.com/watch?v=w-WRZVPM-tg
URL 2: 

Output directory (default: ./transcripts): 

🎬 Transcribing 1 video(s)...

✓ Job submitted: a1b2c3d4-e5f6-7890-abcd-ef1234567890

⏳ Waiting for transcription...
   Status: pending
   Status: processing
   Status: completed

✓ Job finished!

💾 Saving transcripts...

  ✓ w-WRZVPM-tg_20260213_143022.txt

======================================================================
✅ COMPLETE!
======================================================================
Total videos: 1
Completed: 1
Failed: 0

📂 Files saved to: /home/ggonza/Projects/8020-Transcriber/transcripts

   • w-WRZVPM-tg_20260213_143022.txt (45.3 KB)
```

### Example 2: Transcribe Multiple Videos at Once

```bash
python3 transcribe_videos.py \
  "https://www.youtube.com/watch?v=w-WRZVPM-tg" \
  "https://youtu.be/AxNyNHYSN60" \
  "https://youtu.be/dQw4w9WgXcQ"
```

### Example 3: Custom Output Directory

```bash
$ python3 transcribe_videos.py

Enter YouTube URLs (one per line, empty line to finish):

URL 1: https://www.youtube.com/watch?v=w-WRZVPM-tg
URL 2: 

Output directory (default: ./transcripts): ./my_transcripts
```

---

## Troubleshooting

### ❌ "Error: Could not connect to API at http://localhost:5000"

**Solution:** Make sure Flask app is running
```bash
# In another terminal
python app.py
```

### ❌ "401 Unauthorized"

**Solution:** Check API key is correct (default: `dev-api-key-12345`)

### ❌ "Invalid YouTube URL"

**Solution:** Use valid YouTube URLs:
- ✅ `https://www.youtube.com/watch?v=VIDEO_ID`
- ✅ `https://youtu.be/VIDEO_ID`
- ❌ `VIDEO_ID` (alone)

### ❌ Job Stuck in "processing"

**Solution:** Check Celery worker is running
```bash
celery -A celery_app worker --loglevel=info
```

---

## Advanced Usage (Python)

Use it in your own Python code:

```python
from transcribe_videos import SimpleTranscriber

# Create transcriber
transcriber = SimpleTranscriber(
    base_url='http://localhost:5000',
    api_key='dev-api-key-12345'
)

# Transcribe videos
urls = [
    'https://www.youtube.com/watch?v=w-WRZVPM-tg',
    'https://youtu.be/AxNyNHYSN60'
]

job_result = transcriber.transcribe(urls, output_dir='./my_transcripts')

# Save to files
saved_files = transcriber.save_transcripts(job_result, './my_transcripts')

for file in saved_files:
    print(f"Saved: {file}")
```

---

## Tips & Tricks

1. **Faster transcription:** Start multiple Celery workers for parallel processing
2. **Custom output:** Change `./transcripts` to any directory you want
3. **Batch processing:** Pass many URLs at once for bulk transcription
4. **Long videos:** The API waits up to 1 hour by default (configurable)

---

## File Format

Each transcript file includes:
- ✅ Video URL and ID
- ✅ Transcription status
- ✅ Full transcript text
- ✅ Timestamp
- ✅ Error messages (if any)

---

## Need Help?

- **Quick start:** `python3 transcribe_videos.py`
- **See examples:** `python3 example_client.py` (choose option 2)
- **Check API:** `curl http://localhost:5000/` 
- **View logs:** Watch the Flask and Celery terminals

Happy transcribing! 🎬
