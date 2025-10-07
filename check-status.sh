#!/bin/bash

# AI Podcast Generator - Status Check Script
# This script checks the status of all services

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "======================================"
echo "    AI PODCAST GENERATOR STATUS"
echo "======================================"
echo ""

# Function to check HTTP service
check_http() {
    local url=$1
    local name=$2
    local expected_code=$3
    
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1)
    
    if [ "$status_code" = "$expected_code" ]; then
        echo -e "${GREEN}✅ $name${NC} - Running (HTTP $status_code)"
        echo "   URL: ${BLUE}$url${NC}"
        return 0
    else
        echo -e "${RED}❌ $name${NC} - Not responding (HTTP $status_code)"
        echo "   URL: $url"
        return 1
    fi
}

# Check Backend
echo -e "${YELLOW}Backend API:${NC}"
check_http "http://localhost:8000/api/docs" "FastAPI Server" "200"
if pgrep -f "uvicorn main:app" > /dev/null; then
    echo -e "   Process: ${GREEN}Running${NC} (PID: $(pgrep -f 'uvicorn main:app'))"
else
    echo -e "   Process: ${RED}Not running${NC}"
fi
echo ""

# Check Frontend
echo -e "${YELLOW}Frontend:${NC}"
check_http "http://localhost:3000" "Next.js Server" "200"
if pgrep -f "next dev" > /dev/null; then
    echo -e "   Process: ${GREEN}Running${NC} (PID: $(pgrep -f 'next dev'))"
else
    echo -e "   Process: ${RED}Not running${NC}"
fi
echo ""

# Check Redis
echo -e "${YELLOW}Redis:${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis${NC} - Running"
    redis-cli info server | grep "redis_version" | sed 's/redis_version:/   Version: /'
else
    echo -e "${RED}❌ Redis${NC} - Not running"
fi
echo ""

# Check Celery
echo -e "${YELLOW}Celery Worker:${NC}"
if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "${GREEN}✅ Celery Worker${NC} - Running (PID: $(pgrep -f 'celery.*worker'))"
    
    # Check Celery queue status
    if redis-cli -n 0 LLEN celery > /dev/null 2>&1; then
        QUEUE_SIZE=$(redis-cli -n 0 LLEN celery)
        echo "   Queue size: $QUEUE_SIZE tasks"
    fi
else
    echo -e "${RED}❌ Celery Worker${NC} - Not running"
fi
echo ""

# Check Database
echo -e "${YELLOW}PostgreSQL Database:${NC}"
if psql -U akshayram -d ai_podcast_generator -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database${NC} - Connected"
    PODCAST_COUNT=$(psql -U akshayram -d ai_podcast_generator -t -c "SELECT COUNT(*) FROM podcasts;" 2>/dev/null | xargs)
    USER_COUNT=$(psql -U akshayram -d ai_podcast_generator -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | xargs)
    echo "   Podcasts: $PODCAST_COUNT"
    echo "   Users: $USER_COUNT"
else
    echo -e "${RED}❌ Database${NC} - Cannot connect"
fi
echo ""

# Check log files
echo -e "${YELLOW}Log Files:${NC}"
PROJECT_ROOT="/Users/akshayram/Desktop/Projects/new/Ai-pod-generator"

if [ -f "$PROJECT_ROOT/server/server_log.txt" ]; then
    SIZE=$(du -h "$PROJECT_ROOT/server/server_log.txt" | cut -f1)
    echo -e "${GREEN}✅${NC} Backend log: $SIZE"
else
    echo -e "${YELLOW}⚠️${NC}  Backend log: Not found"
fi

if [ -f "$PROJECT_ROOT/server/celery_log.txt" ]; then
    SIZE=$(du -h "$PROJECT_ROOT/server/celery_log.txt" | cut -f1)
    echo -e "${GREEN}✅${NC} Celery log: $SIZE"
else
    echo -e "${YELLOW}⚠️${NC}  Celery log: Not found"
fi

if [ -f "$PROJECT_ROOT/server/client_log.txt" ]; then
    SIZE=$(du -h "$PROJECT_ROOT/server/client_log.txt" | cut -f1)
    echo -e "${GREEN}✅${NC} Frontend log: $SIZE"
else
    echo -e "${YELLOW}⚠️${NC}  Frontend log: Not found"
fi
echo ""

# Port usage
echo -e "${YELLOW}Port Usage:${NC}"
echo "   8000 (Backend):  $(lsof -ti:8000 > /dev/null 2>&1 && echo -e '${GREEN}In use${NC}' || echo -e '${RED}Free${NC}')"
echo "   3000 (Frontend): $(lsof -ti:3000 > /dev/null 2>&1 && echo -e '${GREEN}In use${NC}' || echo -e '${RED}Free${NC}')"
echo "   6379 (Redis):    $(lsof -ti:6379 > /dev/null 2>&1 && echo -e '${GREEN}In use${NC}' || echo -e '${RED}Free${NC}')"
echo "   5432 (Postgres): $(lsof -ti:5432 > /dev/null 2>&1 && echo -e '${GREEN}In use${NC}' || echo -e '${RED}Free${NC}')"
echo ""

echo "======================================"
echo ""
