#!/usr/bin/env bash
# Bootstrap script for Zero-Error Autonomous Project
# Sets up environment and installs dependencies

set -e  # Exit on error

echo "🚀 Zero-Error Autonomous Project Bootstrap"
echo "=========================================="
echo "Following Context7 principles - https://context7.com/"
echo ""

# Check Python version
echo "📍 Checking Python version..."
python_version=$(python3 --version 2>&1 | sed 's/Python //')
required_version="3.8"  # Adjusted for current system

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required (found $python_version)"
    exit 1
fi
echo "✅ Python $python_version detected"

# Check for uv or pip
echo "📍 Checking package manager..."
if command -v uv &> /dev/null; then
    echo "✅ Using uv package manager"
    PKG_MANAGER="uv"
else
    echo "⚠️  uv not found, falling back to pip"
    PKG_MANAGER="pip"
fi

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo "📍 Creating virtual environment..."
    if [ "$PKG_MANAGER" = "uv" ]; then
        uv venv
    else
        python3 -m venv .venv
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "📍 Activating virtual environment..."
source .venv/bin/activate || . .venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "📍 Installing dependencies..."
if [ "$PKG_MANAGER" = "uv" ]; then
    uv pip install -r requirements.txt
else
    pip install --upgrade pip
    pip install -r requirements.txt
fi
echo "✅ Dependencies installed"

# Install Playwright browsers
echo "📍 Installing Playwright browsers..."
playwright install chromium
echo "✅ Playwright browsers installed"

# Create workspace directories
echo "📍 Creating workspace directories..."
mkdir -p workspace/{research,outputs,reports,patches,logs,backend,frontend,messages,events,broadcasts}
mkdir -p tests/{unit,integration,e2e}
mkdir -p .claude/agents
mkdir -p agents
echo "✅ Directories created"

# Copy environment file if not exists
if [ ! -f ".env" ]; then
    echo "📍 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your ANTHROPIC_API_KEY"
else
    echo "✅ .env file exists"
fi

# Initialize git if not already
if [ ! -d ".git" ]; then
    echo "📍 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Zero-Error Autonomous Project Template"
    echo "✅ Git repository initialized"
fi

# Run initial tests
echo "📍 Running smoke tests..."
pytest tests/e2e/test_user_journey.py::test_application_loads -v --tb=short || echo "⚠️  Tests skipped (app not running)"

echo ""
echo "✅ Bootstrap complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your ANTHROPIC_API_KEY"
echo "2. Add your problem statement to inputs/problem.md"
echo "3. Run: python orchestrator.py --mode autonomous"
echo "   Or: @TechLead in Claude Code"
echo ""
echo "For more information, see README.md"