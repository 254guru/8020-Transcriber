# YTScriptify: YouTube Video Transcription API  

## 📌 Project Overview  
**YTScriptify** is a **Flask-based REST API** that transcribes YouTube videos into text using the **YouTube Transcript API**. It follows an **asynchronous Request-Reply pattern** with a **callback mechanism**, allowing users to submit transcription jobs and receive results once processing is complete.  

## 🚀 Features  
- ✅ **Asynchronous Processing** – Users submit YouTube URLs and receive a job ID immediately.  
- ✅ **Callback Mechanism** – The API sends transcription results to the provided callback URL.  
- ✅ **YouTube Link Handling** – Extracts valid YouTube **video IDs** from different URL formats.  
- ✅ **Job Status Tracking** – Check transcription progress using a dedicated **job status endpoint**.  
- ✅ **Error Handling** – Gracefully manages missing transcripts, invalid URLs, and API failures.  

## 🛠 API Endpoints  
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/transcribe` | Accepts a list of YouTube URLs and a callback URL, returns a job ID. |
| `GET` | `/job_status/{job_id}` | Retrieves the status and transcript of a specific job. |
| `POST` | `/transcribe/callback/{job_id}` | Receives completed transcripts via callback. |

## ⚙️ Tech Stack  
- **Backend:** Python, Flask  
- **Transcription:** YouTube Transcript API  
- **Requests Handling:** Flask & `requests` library  
- **Storage:** In-memory (for job tracking)  

## 📌 Example Workflow  
1. **Submit a transcription request** with YouTube URLs.  
2. The API **returns a job ID** while processing the transcription.  
3. **Poll the** `GET /job_status/{job_id}` **endpoint for updates**.  
4. Once completed, the API **sends results to the callback URL**.  

## 🚀 Usage Example  

### 1️⃣ Submit a Transcription Request  
```bash
curl -X POST "http://127.0.0.1:5000/transcribe" \
     -H "Content-Type: application/json" \
     -d '{
           "youtube_urls": ["https://youtu.be/AxNyNHYSN60"], 
           "callback_url": "http://127.0.0.1:5000/transcribe/callback/1234"
         }'

📌 Response:

{
  "job_id": "e8419ddb-6a14-4f1f-9e86-c22782a65599"
}
```
### 2️⃣ Check Job Status
```bash
curl -X GET "http://127.0.0.1:5000/job_status/e8419ddb-6a14-4f1f-9e86-c22782a65599"

📌 Response
{
  "status": "in_progress"
}

or

📌 Response
{
  "status": "completed",
  "transcripts": [
    {
      "url": "https://youtu.be/AxNyNHYSN60",
      "transcript": "This is an example transcript..."
    }
  ]
}

```
