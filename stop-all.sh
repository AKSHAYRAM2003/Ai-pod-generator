#!/bin/bash

# AI Podcast Generator - Shutdown Script
# This script stops all services

echo "🛑 Stopping AI Podcast Generator..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Stop Backend
echo -e "${YELLOW}Stopping Backend Server...${NC}"
if pgrep -f "uvicorn main:app" > /dev/null; then
    pkill -f "uvicorn main:app"
    echo -e "${GREEN}✅ Backend stopped${NC}"
else
    echo -e "${YELLOW}⚠️  Backend was not running${NC}"
fi

# Stop Celery
echo -e "${YELLOW}Stopping Celery Worker...${NC}"
if pgrep -f "celery -A app.core.celery_app worker" > /dev/null; then
    pkill -f "celery -A app.core.celery_app worker"
    echo -e "${GREEN}✅ Celery stopped${NC}"
else
    echo -e "${YELLOW}⚠️  Celery was not running${NC}"
fi

# Stop Frontend
echo -e "${YELLOW}Stopping Frontend...${NC}"
if pgrep -f "next dev" > /dev/null; then
    pkill -f "next dev"
    echo -e "${GREEN}✅ Frontend stopped${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend was not running${NC}"
fi

# Optional: Stop Redis (uncomment if you want to stop Redis too)
# echo -e "${YELLOW}Stopping Redis...${NC}"
# brew services stop redis
# echo -e "${GREEN}✅ Redis stopped${NC}"

echo ""
echo -e "${GREEN}✅ All services stopped successfully!${NC}"
echo ""
echo "To start services again, run: ./start-all.sh"
echo ""
