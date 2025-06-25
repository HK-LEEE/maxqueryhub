#!/bin/bash

echo "Starting Query Hub services..."

# Start backend in background
echo "Starting backend server..."
./start_backend.sh &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 5

# Start frontend
echo "Starting frontend server..."
./start_frontend.sh &
FRONTEND_PID=$!

echo "Services started!"
echo "Backend PID: $BACKEND_PID (http://localhost:8006)"
echo "Frontend PID: $FRONTEND_PID (http://localhost:3006)"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait