# YTScriptify - Documentation Quick Reference

## 📍 Which Document Do I Need?

### I want to...
- **Install/Setup** → [SETUP.md](SETUP.md)
- **Understand the architecture** → [README.md](README.md)
- **Transcribe videos** → [HOW_TO_USE.md](HOW_TO_USE.md)
- **Deploy to production** → [DEPLOYMENT.md](DEPLOYMENT.md)
- **Use the API in my code** → [example_client.py](example_client.py)
- **See refactoring improvements** → [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
- **Transcribe & save files** → `python3 transcribe_videos.py`

---

## 🚀 Quick Commands

### Install
```bash
pip install -r requirements.txt
docker-compose up -d
```

### Run Services
```bash
celery -A celery_app worker --loglevel=info    # Terminal 1
python app.py                                   # Terminal 2
python3 transcribe_videos.py                   # Terminal 3
```

### Check Health
```bash
curl http://localhost:5000/
```

### Transcribe Videos
```bash
python3 transcribe_videos.py
```

---

## 📂 File Structure

```
8020-Transcriber/
├── SETUP.md                  ← Installation (START HERE)
├── README.md                 ← Features & API endpoints
├── HOW_TO_USE.md            ← How to transcribe videos
├── DEPLOYMENT.md            ← Production deployment
├── REFACTORING_SUMMARY.md   ← Code quality improvements
│
├── client.py                ← Shared API client (NEW)
├── app.py                   ← Flask API
├── celery_app.py           ← Background worker
├── models.py               ← Database models
├── config.py               ← Configuration
│
├── transcribe_videos.py    ← CLI tool (use this!)
├── example_client.py       ← API examples (for development)
├── test_videos.py          ← Test video URLs
│
├── requirements.txt        ← Python dependencies
├── docker-compose.yml      ← Docker services
├── .env                    ← Environment variables
└── .env.example           ← Template
```

---

## 🔑 Key Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/transcribe` | Submit transcription job |
| GET | `/job_status/{id}` | Check job status |
| GET | `/jobs` | List all jobs |
| DELETE | `/job_status/{id}` | Cancel job |

All require: `-H "X-API-Key: dev-api-key-12345"`

---

## ⚙️ Configuration

Key settings in `.env`:
```env
API_KEY=dev-api-key-12345
FLASK_ENV=development
DATABASE_URL=sqlite:///transcriber.db
CELERY_BROKER_URL=redis://localhost:6379/0
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect to Redis | Run `docker-compose up -d` or `redis-server` |
| API returns 401 | Check API key in request header |
| Celery worker not running | Run `celery -A celery_app worker --loglevel=info` |
| Video has no captions | Use TED Talks or Khan Academy (run `python3 test_videos.py`) |

---

## 🏗️ Architecture Improvements

✅ **Shared API Client** (`client.py`) - Eliminated 60+ lines of duplicate code
✅ **Clean Separation** - Each tool has single clear purpose:
   - `client.py` - Reusable API client library
   - `transcribe_videos.py` - CLI tool for end users
   - `example_client.py` - API examples for developers
✅ **Easy Maintenance** - API changes in one place
✅ **Better Testing** - Can test client independently

See [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) for details.

