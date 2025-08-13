#!/bin/bash

# ClinicLite Botswana - Startup Script

echo "Starting ClinicLite Botswana..."

# Check Python version
python3 --version

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip3 install -r requirements.txt

# Start backend server
echo "Starting backend server on port 8000..."
python3 main.py &
BACKEND_PID=$!

# Start frontend server
echo "Starting frontend server on port 3000..."
cd ../frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!

echo "ClinicLite is running!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop..."

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait