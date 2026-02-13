# YTScriptify Deployment & Operations Guide

## Quick Start

**For all setup scenarios (Docker, Local Redis, Manual):** See [SETUP.md](SETUP.md)

This guide covers **production deployment, scaling, and operations**.

---

## Key Improvements Made

**See [README.md](README.md#-architecture-v20-improvements) for detailed improvements (async, persistence, security, etc.)**

---

## Configuration

All configuration is centralized in `config.py` and `.env`:

```env
# Flask
FLASK_ENV=development|production
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///transcriber.db
# or: postgresql://user:pass@host:port/dbname

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# API
API_KEY=your-api-key
REQUEST_LIMIT=100/hour

# Jobs
JOB_TIMEOUT=3600
MAX_URLS_PER_JOB=50
```

---

## Database Schema

### Jobs Table
```sql
CREATE TABLE jobs (
  id VARCHAR(36) PRIMARY KEY,          -- UUID
  status VARCHAR(20),                  -- pending|processing|completed|failed|cancelled
  created_at DATETIME,
  updated_at DATETIME,
  callback_url VARCHAR(500),
  error_message TEXT
);
```

### Transcripts Table
```sql
CREATE TABLE transcripts (
  id INTEGER PRIMARY KEY,
  job_id VARCHAR(36) FOREIGN KEY,
  url VARCHAR(500),
  video_id VARCHAR(20),
  transcript_data TEXT,                -- JSON string
  status VARCHAR(20),                  -- pending|completed|failed
  error_message TEXT,
  created_at DATETIME,
  updated_at DATETIME
);
```

---

## API Workflow

### Normal Flow
```
1. Client: POST /transcribe
   └─ API validates & creates Job (status=pending)
   └─ API queues Celery task
   └─ API returns 202 Accepted + job_id

2. Celery Worker (background)
   └─ Picks up task from Redis queue
   └─ Updates Job status to "processing"
   └─ Transcribes each video
   └─ Stores results in database
   └─ Updates Job status to "completed"
   └─ Sends callback to client_callback_url

3. Client: Polls /job_status/{job_id}
   └─ Gets current status & results
```

### Error Flow
```
If transcription fails:
└─ Transcript marked with status=failed + error_message
└─ Job status remains pending if other URLs still processing
└─ Job status becomes failed if all URLs fail
└─ Callback still sent with partial/error results
```

---

## Production Checklist

- [ ] Change `API_KEY` to a strong value
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `FLASK_ENV=production`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Use `gunicorn` or similar production WSGI server
- [ ] Set up multiple Celery workers for concurrency
- [ ] Configure proper logging to files
- [ ] Set up monitoring/alerting for job failures
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS for all API calls
- [ ] Set up backup strategy for database
- [ ] Configure rate limiting based on expected load

---

## Running in Production

### Using Systemd Services

**Flask Service** (`/etc/systemd/system/ytscriptify.service`):
```ini
[Unit]
Description=YTScriptify Flask API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/ytscriptify
Environment="PATH=/opt/ytscriptify/.venv/bin"
ExecStart=/opt/ytscriptify/.venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Celery Worker Service** (`/etc/systemd/system/ytscriptify-worker.service`):
```ini
[Unit]
Description=YTScriptify Celery Worker
After=network.target redis.service

[Service]
User=www-data
WorkingDirectory=/opt/ytscriptify
Environment="PATH=/opt/ytscriptify/.venv/bin"
ExecStart=/opt/ytscriptify/.venv/bin/celery -A celery_app worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

Start services:
```bash
sudo systemctl start ytscriptify
sudo systemctl start ytscriptify-worker
sudo systemctl enable ytscriptify ytscriptify-worker
```

---

## Monitoring

### Check Job Queue
```bash
celery -A celery_app inspect active
celery -A celery_app inspect stats
```

### Check Database
```bash
# SQLite
sqlite3 transcriber.db "SELECT status, COUNT(*) FROM jobs GROUP BY status;"

# PostgreSQL
psql -U transcriber -d transcriber -c "SELECT status, COUNT(*) FROM jobs GROUP BY status;"
```

### Logs
```bash
# Flask logs (if running with systemd)
journalctl -u ytscriptify -f

# Celery worker logs
journalctl -u ytscriptify-worker -f
```

---

## Troubleshooting

### "Connection refused" on Redis
```bash
# Check if Redis is running
redis-cli ping

# If using Docker
docker-compose ps
docker-compose logs redis
```

### "Module not found" errors
```bash
# Ensure you're in correct venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Jobs stuck in "processing"
```bash
# Check worker status
celery -A celery_app inspect active

# Restart worker
pkill -f celery
celery -A celery_app worker --loglevel=info
```

### Database locked (SQLite)
```bash
# Reset database (WARNING: deletes all jobs)
rm transcriber.db
python -c "from models import db; from app import app; app.app_context().push(); db.create_all()"
```

---

## Scaling

### Multiple Workers
```bash
# Worker 1
celery -A celery_app worker -n worker1@%h --concurrency=4

# Worker 2 (different machine)
celery -A celery_app worker -n worker2@%h --concurrency=4
```

### Load Balancing (Nginx)
```nginx
upstream ytscriptify {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
}

server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://ytscriptify;
    }
}
```

---

## License
MIT
