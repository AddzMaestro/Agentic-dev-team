#!/bin/bash

# Launch ClinicLite No-Show Prediction System

echo "🚀 Launching ClinicLite No-Show Prediction System..."
echo "=================================================="

# Check if backend is running
if curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
    echo "✅ Backend is running on port 8000"
else
    echo "⚠️  Backend is not running. Please start it with:"
    echo "   cd workspace/backend && python3 -m uvicorn main:app --reload"
    exit 1
fi

# URLs to open
MAIN_URL="http://localhost:8000/static/"
TEST_URL="http://localhost:8000/static/test-predictions.html"

echo ""
echo "📋 Available Pages:"
echo "-------------------"
echo "1. Main Dashboard:      $MAIN_URL"
echo "2. Test Components:     $TEST_URL"
echo ""

# Detect OS and open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Opening in default browser (macOS)..."
    open "$MAIN_URL"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Opening in default browser (Linux)..."
    xdg-open "$MAIN_URL"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows
    echo "Opening in default browser (Windows)..."
    start "$MAIN_URL"
else
    echo "Please open your browser and navigate to:"
    echo "  $MAIN_URL"
fi

echo ""
echo "✨ Application launched successfully!"
echo ""
echo "📌 Quick Navigation:"
echo "  - Click 'Predictions' tab to see the No-Show Prediction System"
echo "  - Risk scores are displayed with color coding (Green/Yellow/Orange/Red)"
echo "  - Pattern analysis shows peak no-show times"
echo "  - Smart scheduling recommendations are in the Dashboard view"
echo ""
echo "Press Ctrl+C in the backend terminal to stop the server."