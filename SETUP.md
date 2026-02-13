# 🚀 YTScriptify Setup Guide

**This is the single source of truth for all setup scenarios.**

## Quick Start (5 minutes)

### Prerequisites
- Python 3.8+
- Docker (or local Redis)
- Internet connection

### Installation

```bash
# 1. Clone and enter directory
cd 8020-Transcriber

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env

# 5. Start services
docker-compose up -d          # Starts Redis & PostgreSQL
```

### Running the System

**Terminal 1: Celery Worker**
```bash
celery -A celery_app worker --loglevel=info
```

**Terminal 2: Flask API**
```bash
python app.py
```

**Terminal 3: Transcribe Videos**
```bash
python3 transcribe_videos.py
```

---

## Setup Scenarios

### Scenario A: Docker (Recommended for Production)

```bash
# Start all services
docker compose up -d

# Install Python dependencies
pip install -r requirements.txt

# Start Flask and Celery (in separate terminals)
celery -A celery_app worker --loglevel=info
python app.py
```

**Services started:**
- Redis on `localhost:6379`
- PostgreSQL on `localhost:5432`
- Flask API on `localhost:5000`

---

### Scenario B: Local Redis Only (Development)

```bash
# Start Redis locally
redis-server

# Install dependencies
pip install -r requirements.txt

# Configure SQLite database (default in .env)
# DATABASE_URL=sqlite:///transcriber.db

# Start services
celery -A celery_app worker --loglevel=info
python app.py
```

---

### Scenario C: Manual Setup (No Docker)

```bash
# 1. Ensure Redis is running
redis-server  # or install via: brew install redis

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Ensure .env exists
cp .env.example .env  # if needed

# 5. Start in separate terminals
celery -A celery_app worker --loglevel=info
python app.py
```

---

## Verification

### Check API is Running
```bash
curl http://localhost:5000/
# Should return: {"status": "ok"}
```

### Check Celery Worker
```bash
# Should show: "celery@hostname ready"
```

### Submit a Test Job
```bash
curl -X POST "http://localhost:5000/transcribe" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-12345" \
  -d '{"urls": ["https://youtu.be/jNQXAC9IVRw"]}'
```

---

## Configuration

All settings in `.env`:

```env
# API
FLASK_ENV=development
API_KEY=dev-api-key-12345
REQUEST_LIMIT=100/hour

# Database (choose one)
DATABASE_URL=sqlite:///transcriber.db              # Development
# DATABASE_URL=postgresql://user:pass@host/dbname # Production

# Celery & Message Broker
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Job Processing
JOB_TIMEOUT=3600
MAX_URLS_PER_JOB=50
```

**To use PostgreSQL:** Update `DATABASE_URL` and restart services.

---

## First-Time Troubleshooting

| Error | Solution |
|-------|----------|
| `ConnectionRefusedError: Redis` | Start Redis: `redis-server` or `docker-compose up -d redis` |
| `ModuleNotFoundError: flask` | Activate venv: `source .venv/bin/activate` then `pip install -r requirements.txt` |
| `Celery worker not picking up tasks` | Ensure `CELERY_BROKER_URL` points to running Redis |
| `API returns 401 Unauthorized` | Check API key in request header: `X-API-Key: dev-api-key-12345` |
| `Video has no captions` | Use videos from TED, Khan Academy, or news channels (run `python3 test_videos.py`) |

---

## What Gets Created

| File | Purpose |
|------|---------|
| `transcriber.db` | SQLite database (if using SQLite) |
| `transcripts/` | Directory with saved transcript `.txt` files |
| `instance/` | Flask instance folder |

---

## Next Steps

1. **Transcribe videos:** `python3 transcribe_videos.py`
2. **Check status:** `curl -H "X-API-Key: dev-api-key-12345" http://localhost:5000/jobs`
3. **Scale workers:** Run `celery -A celery_app worker -n worker2@%h` for parallel processing
4. **Deploy to production:** See [README.md](README.md) architecture section for production setup

---

## Documentation Map

| File | Contents |
|------|----------|
| **SETUP.md** (this file) | Installation for all scenarios |
| **README.md** | Architecture, API endpoints, features |
| **HOW_TO_USE.md** | How to transcribe videos using CLI tools |
| **DEPLOYMENT.md** | Production deployment and operations |

