#!/bin/bash

# Indian Stock Market Analytics - Quick Start Script

echo "=================================================="
echo "Indian Stock Market Analytics Dashboard"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    echo "Please install pip3"
    exit 1
fi

echo -e "${GREEN}✓ pip3 found${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    echo "Please check requirements.txt and try again"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}Please edit .env file with your API keys${NC}"
fi

# Check if Redis is running (optional)
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠ Redis is not running (caching will be disabled)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Redis not installed (caching will be disabled)${NC}"
fi

# Create necessary directories
mkdir -p logs
mkdir -p data
mkdir -p models

echo ""
echo "=================================================="
echo "Starting API Server..."
echo "=================================================="
echo ""
echo "API will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the API server
python3 api_server.py
