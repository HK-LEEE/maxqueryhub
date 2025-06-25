#!/bin/bash

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env file with your configuration before running!"
    echo "   Especially set the JWT_SECRET_KEY to match your maxplatform key"
    exit 1
fi

# Check if database URL is configured
if grep -q "password@localhost" .env; then
    echo "⚠️  Warning: Using default database password in .env"
    echo "   Please update DATABASE_URL with your actual credentials"
fi

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || echo "⚠️  Migration failed - make sure database is created and accessible"

# Start the server
echo "Starting Query Hub Backend on port 8006..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8006