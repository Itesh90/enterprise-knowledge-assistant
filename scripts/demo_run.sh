#!/usr/bin/env bash
set -euo pipefail

# Enterprise Knowledge Assistant - Local Demo Script
# This script automates the local bring-up process

echo "=== Enterprise Knowledge Assistant - Demo Run ==="
echo ""

cd "$(dirname "$0")/.."

# Check prerequisites
if ! command -v python3 &> /dev/null; then
  echo "Error: python3 not found"
  exit 1
fi

if ! command -v pnpm &> /dev/null && ! command -v npm &> /dev/null; then
  echo "Error: pnpm or npm required"
  exit 1
fi

# Backend setup
echo "=== Backend Setup ==="
cd backend

if [ ! -f .env ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
  echo "⚠️  Please edit backend/.env and add OPENAI_API_KEY (optional)"
fi

if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
fi

echo "Installing backend dependencies..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
pip install -q -r requirements.txt

echo "Building index from seed data..."
python -m app.ingest.build_index --paths backend/data/raw --max-chunk-tokens 512 --overlap 64 || {
  echo "⚠️  Index build failed. Continuing anyway..."
}

echo ""
echo "✅ Backend ready. Run: cd backend && source venv/bin/activate && uvicorn app.api.main:app --reload --port 8000"
echo ""

# Frontend setup
echo "=== Frontend Setup ==="
cd ../frontend

if [ ! -f .env ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
fi

if command -v pnpm &> /dev/null; then
  echo "Installing frontend dependencies with pnpm..."
  pnpm install --silent
  PM_CMD="pnpm"
else
  echo "Installing frontend dependencies with npm..."
  npm install --silent
  PM_CMD="npm"
fi

echo ""
echo "✅ Frontend ready. Run: cd frontend && $PM_CMD dev"
echo ""
echo "=== Demo Setup Complete ==="
echo ""
echo "To start:"
echo "  1. Terminal 1: cd backend && source venv/bin/activate && uvicorn app.api.main:app --reload --port 8000"
echo "  2. Terminal 2: cd frontend && $PM_CMD dev"
echo "  3. Open http://localhost:3000"
echo ""

