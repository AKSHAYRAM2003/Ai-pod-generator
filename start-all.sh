#!/bin/bash

# AI Podcast Generator - Startup Script
# This script starts all required services for the application

echo "🚀 Starting AI Podcast Generator..."
echo ""

# Navigate to project root
cd "$(dirname "$0")"
PROJECT_ROOT="/Users/akshayram/Desktop/Projects/new/Ai-pod-generator"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a port is in use
port_in_use() {
    lsof -ti:$1 > /dev/null 2>&1
}

# Function to check if a service is running
check_service() {
    if curl -s -o /dev/null -w "%{http_code}" "$1" | grep -q "$2"; then
        echo -e "${GREEN}✅ $3 is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $3 is not responding${NC}"
        return 1
    fi
}

# 1. Check and start Redis
echo -e "${YELLOW}Checking Redis...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is already running${NC}"
else
    echo "Starting Redis..."
    brew services start redis
    sleep 2
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start Redis${NC}"
        exit 1
    fi
fi
echo ""

# 2. Start Backend Server
echo -e "${YELLOW}Starting Backend Server...${NC}"
if port_in_use 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use. Stopping existing process...${NC}"
    pkill -f "uvicorn main:app"
    sleep 2
fi

cd "$PROJECT_ROOT/server"
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > server_log.txt 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo ""

# 3. Start Celery Worker
echo -e "${YELLOW}Starting Celery Worker...${NC}"
if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "${YELLOW}⚠️  Celery worker is already running. Stopping existing process...${NC}"
    pkill -f "celery -A app.core.celery_app worker"
    sleep 2
fi

celery -A app.core.celery_app worker --loglevel=info --pool=solo > celery_log.txt 2>&1 &
CELERY_PID=$!
echo -e "${GREEN}✅ Celery started (PID: $CELERY_PID)${NC}"
echo ""

# 4. Start Frontend
echo -e "${YELLOW}Starting Frontend...${NC}"
if port_in_use 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use. Stopping existing process...${NC}"
    pkill -f "next dev"
    sleep 2
fi

cd "$PROJECT_ROOT/client"
npm run dev > ../server/client_log.txt 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 8

# Check service status
echo ""
echo "======================================"
echo "         SERVICE STATUS"
echo "======================================"
echo ""

# Check Backend
check_service "http://localhost:8000/api/docs" "200" "Backend API"

# Check Frontend
check_service "http://localhost:3000" "200" "Frontend"

# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not responding${NC}"
fi

# Check Celery
if ps aux | grep "celery.*worker" | grep -v grep > /dev/null; then
    echo -e "${GREEN}✅ Celery Worker is running${NC}"
else
    echo -e "${RED}❌ Celery Worker is not running${NC}"
fi

echo ""
echo "======================================"
echo "         ACCESS POINTS"
echo "======================================"
echo ""
echo -e "🌐 Frontend:     ${GREEN}http://localhost:3000${NC}"
echo -e "📚 API Docs:     ${GREEN}http://localhost:8000/api/docs${NC}"
echo -e "📊 ReDoc:        ${GREEN}http://localhost:8000/api/redoc${NC}"
echo ""
echo "======================================"
echo "         PROCESS IDs"
echo "======================================"
echo ""
echo "Backend:  $BACKEND_PID"
echo "Celery:   $CELERY_PID"
echo "Frontend: $FRONTEND_PID"
echo ""
echo "======================================"
echo "         LOG FILES"
echo "======================================"
echo ""
echo "Backend:  $PROJECT_ROOT/server/server_log.txt"
echo "Celery:   $PROJECT_ROOT/server/celery_log.txt"
echo "Frontend: $PROJECT_ROOT/server/client_log.txt"
echo ""
echo "View logs: tail -f $PROJECT_ROOT/server/*.txt"
echo ""
echo -e "${GREEN}✅ All services started successfully!${NC}"
echo ""
echo "To stop all services, run: ./stop-all.sh"
echo "Or manually: pkill -f 'uvicorn main:app' && pkill -f 'celery -A app.core.celery_app worker' && pkill -f 'next dev'"
echo ""
