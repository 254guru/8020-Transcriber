from flask import Flask, request, jsonify, abort
from uuid import uuid4
import requests
import re
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

# In-memory storage for job_id to transcript mapping
job_store = {}

def extract_video_id(url):
    """
    Extracts the YouTube video ID from various URL formats.
    """
    pattern = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route('/')
def home():
    return "Welcome to YTScriptify API! Use /transcribe to submit a job.", 200

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        data = request.json
        youtube_urls = data.get('youtube_urls', [])
        callback_url = data.get('callback_url')

        if not youtube_urls or not callback_url:
            abort(400, 'Missing required parameters')

        job_id = str(uuid4())
        job_store[job_id] = {'status': 'in_progress', 'transcripts': []}

        for url in youtube_urls:
            video_id = extract_video_id(url)
            if not video_id:
                job_store[job_id]['transcripts'].append({'url': url, 'transcript': "Invalid YouTube URL."})
                continue  # Skip processing this URL

            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                job_store[job_id]['transcripts'].append({'url': url, 'transcript': transcript})
            except Exception as e:
                job_store[job_id]['transcripts'].append({'url': url, 'transcript': str(e)})

        # Send async callback
        requests.post(callback_url, json={'job_id': job_id})

        return jsonify({'job_id': job_id}), 200

    except Exception as e:
        abort(500, str(e))

@app.route('/job_status/<job_id>', methods=['GET'])
def job_status(job_id):
    """
    Retrieves the status of a transcription job.
    """
    if job_id not in job_store:
        abort(404, 'Job ID not found')

    return jsonify(job_store[job_id]), 200

@app.route('/transcribe/callback/<job_id>', methods=['POST'])
def callback(job_id):
    try:
        data = request.json
        full_transcript = data.get('full_transcript')

        if job_id not in job_store:
            abort(404, 'Job ID not found')

        job_store[job_id]['status'] = 'completed'
        job_store[job_id]['full_transcript'] = full_transcript

        return jsonify({'message': 'Callback received successfully'}), 200

    except Exception as e:
        abort(500, str(e))

if __name__ == '__main__':
    app.run(debug=True)

