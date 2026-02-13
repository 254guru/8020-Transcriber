# YTScriptify: YouTube Video Transcription API (v2.0)

## 📌 Project Overview  
**YTScriptify** is an **async-first Flask REST API** that transcribes YouTube videos into text using the **YouTube Transcript API**. It implements a **true asynchronous processing pattern** with **Celery workers**, **Redis message queue**, **SQLAlchemy persistence**, and **callback notifications** for completed jobs.

## 🎯 Architecture (v2.0 Improvements)

### Key Features
- ✅ **True Asynchronous Processing** – Jobs are queued immediately; transcription happens in background workers
- ✅ **Database Persistence** – SQLite/PostgreSQL stores all jobs and transcripts (survives restarts)
- ✅ **Celery Workers** – Distributed task processing with retry logic and error handling
- ✅ **Redis Queue** – Fast message broker for reliable job queueing
- ✅ **Smart Callbacks** – Results sent to your endpoint AFTER processing completes
- ✅ **Job Lifecycle** – pending → processing → completed/failed states with timestamps
- ✅ **API Key Authentication** – Secure endpoints with X-API-Key headers
- ✅ **Rate Limiting** – Prevent abuse with configurable request limits
- ✅ **Structured Logging** – Full visibility into API operations and worker tasks
- ✅ **Job Management** – List, check status, and cancel jobs via REST API

## 🛠 Tech Stack  
- **Backend:** Python 3.8+, Flask 3.0
- **Task Queue:** Celery 5.3
- **Message Broker:** Redis 5.0
- **Database:** SQLAlchemy 2.0 with SQLite/PostgreSQL
- **Transcription:** YouTube Transcript API
- **Security:** API Key authentication, Rate Limiting
- **Logging:** Python logging module

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.8+
- Redis server running locally or accessible via network
- pip and virtualenv

### 1. Clone and Setup Environment
```bash
git clone <your-repo>
cd 8020-Transcriber
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env and set your own API_KEY and SECRET_KEY
```

### 3. Start Redis (Required)
```bash
# Option 1: Using Docker
docker run -d -p 6379:6379 redis:latest

# Option 2: Local Redis installation
redis-server
```

### 4. Start Celery Worker
```bash
# In a separate terminal, from project root
celery -A celery_app worker --loglevel=info
```

### 5. Start Flask Application
```bash
# In another terminal
python app.py
```

The API will be available at `http://localhost:5000`

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|---------|-------------|------|
| `POST` | `/transcribe` | Submit a transcription job | ✅ Required |
| `GET` | `/job_status/{job_id}` | Get job status and results | ✅ Required |
| `GET` | `/jobs` | List all jobs with pagination | ✅ Required |
| `DELETE` | `/job_status/{job_id}` | Cancel a pending job | ✅ Required |
| `GET` | `/` | Health check | ❌ Optional |

## 🔐 Authentication

All endpoints (except `/`) require an API key in the header:

```bash
curl -X GET "http://localhost:5000/job_status/your-job-id" \
     -H "X-API-Key: dev-api-key-12345"
```

## 📚 Usage Examples

### 1️⃣ Submit a Transcription Request
```bash
curl -X POST "http://localhost:5000/transcribe" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: dev-api-key-12345" \
     -d '{
       "youtube_urls": [
         "https://youtu.be/AxNyNHYSN60",
         "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
       ],
       "callback_url": "https://your-app.com/webhook/transcription"
     }'
```

**Response (202 Accepted):**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "pending",
  "message": "Transcription job queued. Check status using the job_id."
}
```

### 2️⃣ Check Job Status
```bash
curl -X GET "http://localhost:5000/job_status/f47ac10b-58cc-4372-a567-0e02b2c3d479" \
     -H "X-API-Key: dev-api-key-12345"
```

### 3️⃣ List All Jobs
```bash
curl -X GET "http://localhost:5000/jobs?page=1&per_page=10" \
     -H "X-API-Key: dev-api-key-12345"
```

### 4️⃣ Cancel a Job
```bash
curl -X DELETE "http://localhost:5000/job_status/f47ac10b-58cc-4372-a567-0e02b2c3d479" \
     -H "X-API-Key: dev-api-key-12345"
```

## 📊 Job Status States

- **pending** – Job created, waiting for worker pickup
- **processing** – Worker is actively transcribing videos
- **completed** – All videos transcribed successfully
- **failed** – An error occurred during processing
- **cancelled** – Job was manually cancelled

## 🚀 Production Deployment

### Using Gunicorn + Systemd

1. **Start Flask with Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **Start Celery Worker:**
```bash
celery -A celery_app worker --loglevel=info --concurrency=4
```

3. **Use PostgreSQL instead of SQLite:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/transcriber
```

## 📝 License
MIT

## 🤝 Contributing
Pull requests welcome! Please test thoroughly and update documentation.
