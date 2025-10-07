# 🎙️ AI Podcast Generator - Quick Start Guide

**All services are currently running!** ✅

---

## 🚀 Quick Commands

### Start All Services
```bash
cd /Users/akshayram/Desktop/Projects/new/Ai-pod-generator
./start-all.sh
```

### Stop All Services
```bash
cd /Users/akshayram/Desktop/Projects/new/Ai-pod-generator
./stop-all.sh
```

### Check Status
```bash
cd /Users/akshayram/Desktop/Projects/new/Ai-pod-generator
./check-status.sh
```

---

## 🌐 Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main web application |
| **API Docs** | http://localhost:8000/api/docs | Swagger API documentation |
| **ReDoc** | http://localhost:8000/api/redoc | Alternative API docs |

---

## 📊 Current Status

### Running Services:
- ✅ **Backend** (FastAPI) - Port 8000
- ✅ **Frontend** (Next.js) - Port 3000  
- ✅ **Celery Worker** - Background tasks
- ✅ **Redis** - Message broker
- ✅ **PostgreSQL** - Database

### To verify everything is working:
```bash
./check-status.sh
```

---

## 📝 View Logs

### All Logs (Live)
```bash
cd /Users/akshayram/Desktop/Projects/new/Ai-pod-generator/server
tail -f server_log.txt celery_log.txt client_log.txt
```

### Individual Logs
```bash
# Backend log
tail -f server/server_log.txt

# Celery log
tail -f server/celery_log.txt

# Frontend log
tail -f server/client_log.txt
```

---

## 🔄 Restart Services

### Restart Everything
```bash
./stop-all.sh && sleep 2 && ./start-all.sh
```

### Restart Individual Services

**Backend only:**
```bash
pkill -f "uvicorn main:app"
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > server_log.txt 2>&1 &
```

**Celery only:**
```bash
pkill -f "celery -A app.core.celery_app worker"
cd server
celery -A app.core.celery_app worker --loglevel=info --pool=solo > celery_log.txt 2>&1 &
```

**Frontend only:**
```bash
pkill -f "next dev"
cd client
npm run dev > ../server/client_log.txt 2>&1 &
```

---

## 🧪 Test Podcast Generation

1. **Open the app**: http://localhost:3000
2. **Sign in** or create an account
3. **Go to "My Pods"** page
4. **Click "Create New Podcast"**
5. Fill in the form:
   - Title: Your choice
   - Topic: Your choice
   - Duration: 5, 7, or 10 minutes
   - Speaker: Single or Two
   - Voice: Male or Female
6. **Click "Generate Podcast"**
7. **Watch the progress bar** update in real-time
8. **Play the podcast** when complete!

---

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Kill all processes and restart
pkill -f "uvicorn main:app"
pkill -f "celery -A app.core.celery_app worker"
pkill -f "next dev"

# Wait a moment
sleep 2

# Start again
./start-all.sh
```

### Check Which Ports Are in Use
```bash
lsof -ti:8000  # Backend
lsof -ti:3000  # Frontend
lsof -ti:6379  # Redis
lsof -ti:5432  # PostgreSQL
```

### Clear Redis Queue
```bash
redis-cli FLUSHALL
```

### Check Podcast Status
```bash
cd /Users/akshayram/Desktop/Projects/new/Ai-pod-generator/server
python3 check_user_podcasts.py
```

---

## 📚 Documentation

- **Full Setup Guide**: [PROJECT_SETUP_GUIDE.md](PROJECT_SETUP_GUIDE.md)
- **Event Loop Fix**: [EVENT_LOOP_FIX.md](EVENT_LOOP_FIX.md)
- **Services Status**: [SERVICES_STATUS.md](SERVICES_STATUS.md)

---

## 🛠️ Development

### Run Manually (Terminal Tabs)

**Tab 1 - Backend:**
```bash
cd /Users/akshayram/Desktop/Projects/new/Ai-pod-generator/server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Tab 2 - Celery:**
```bash
cd /Users/akshayram/Desktop/Projects/new/Ai-pod-generator/server
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

**Tab 3 - Frontend:**
```bash
cd /Users/akshayram/Desktop/Projects/new/Ai-pod-generator/client
npm run dev
```

---

## ⚡ Useful Scripts

| Script | Purpose |
|--------|---------|
| `./start-all.sh` | Start all services in background |
| `./stop-all.sh` | Stop all services |
| `./check-status.sh` | Check status of all services |
| `server/check_user_podcasts.py` | Check podcasts for a user |
| `server/trigger_generation.py` | Manually trigger podcast generation |

---

## 🎯 What's Working

- ✅ User authentication (signup/login)
- ✅ Podcast creation with AI
- ✅ Real-time progress tracking (0% → 100%)
- ✅ Single and two-speaker modes
- ✅ Audio generation with Gemini AI
- ✅ Audio playback
- ✅ Make podcasts public
- ✅ Browse and discover podcasts
- ✅ User profile management
- ✅ Category-based organization

---

## 📋 Environment Variables

**Backend (.env):**
- `DATABASE_URL` - PostgreSQL connection
- `SECRET_KEY` - JWT authentication
- `GEMINI_API_KEY` - Google Gemini API
- `CELERY_BROKER_URL` - Redis URL
- `CELERY_RESULT_BACKEND` - Redis URL

**Frontend (.env.local):**
- `NEXT_PUBLIC_API_URL` - Backend API URL

---

## 🔑 Important Notes

1. **Redis must be running** before starting Celery
2. **Use `--pool=solo` for Celery on macOS** to avoid event loop issues
3. **Backend auto-reloads**, but Celery requires manual restart after code changes
4. **Check logs** if something doesn't work
5. **Database connection** may prompt for password in status check

---

## 🎉 You're All Set!

Open http://localhost:3000 and start creating amazing AI-generated podcasts! 🚀

For any issues, check the logs or refer to [PROJECT_SETUP_GUIDE.md](PROJECT_SETUP_GUIDE.md)

---

**Happy Podcasting! 🎙️✨**
