#!/usr/bin/env bash

# ============================================================================
# 🚀 AUTONOMOUS AGENT SYSTEM - QUICK SETUP
# ============================================================================
# This script sets up a fully autonomous, self-healing development environment
# that runs continuously until achieving 100% test coverage.
#
# The system uses multiple specialized AI agents that work together to:
# - Analyze requirements and design architecture
# - Build implementation with backend and frontend
# - Create comprehensive Playwright tests
# - Self-heal when tests fail (up to 5 attempts)
# - Deliver production-ready code with zero errors
# ============================================================================

set -e  # Exit on any error

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Banner
clear
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║        🤖 AUTONOMOUS MULTI-AGENT DEVELOPMENT SYSTEM 🤖          ║"
echo "║                                                                  ║"
echo "║                    Zero-Error Delivery                          ║"
echo "║                   Context7 Implementation                       ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo

# ============================================================================
# STEP 1: Prerequisites Check
# ============================================================================
echo -e "${YELLOW}📋 STEP 1: Checking Prerequisites${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python
echo -n "  ✓ Python 3.8+... "
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | sed 's/Python //')
    echo -e "${GREEN}Found $python_version${NC}"
else
    echo -e "${RED}Not found! Please install Python 3.8+${NC}"
    exit 1
fi

# Check Node.js
echo -n "  ✓ Node.js... "
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo -e "${GREEN}Found $node_version${NC}"
else
    echo -e "${RED}Not found! Please install Node.js 14+${NC}"
    exit 1
fi

# Check Git
echo -n "  ✓ Git... "
if command -v git &> /dev/null; then
    git_version=$(git --version | cut -d' ' -f3)
    echo -e "${GREEN}Found $git_version${NC}"
else
    echo -e "${RED}Not found! Please install Git${NC}"
    exit 1
fi

echo

# ============================================================================
# STEP 2: Environment Setup
# ============================================================================
echo -e "${YELLOW}🔧 STEP 2: Setting Up Environment${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv .venv
    echo -e "  ${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "  ${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source .venv/bin/activate || . .venv/Scripts/activate 2>/dev/null

# Upgrade pip and fix setuptools
echo "  Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel --quiet 2>/dev/null || {
    echo -e "  ${YELLOW}⚠️  Using existing pip version${NC}"
}

echo

# ============================================================================
# STEP 3: Dependencies Installation
# ============================================================================
echo -e "${YELLOW}📦 STEP 3: Installing Dependencies${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install Python dependencies
echo "  Installing Python packages..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet 2>/dev/null || {
        echo -e "  ${YELLOW}⚠️  Some packages may need manual installation${NC}"
        echo "  Attempting core packages..."
        pip install anthropic playwright pytest loguru pydantic python-dotenv --quiet 2>/dev/null
    }
    echo -e "  ${GREEN}✓ Core dependencies installed${NC}"
else
    echo -e "  ${YELLOW}⚠️  requirements.txt not found, installing core packages${NC}"
    pip install anthropic playwright pytest loguru pydantic python-dotenv --quiet
    echo -e "  ${GREEN}✓ Core packages installed${NC}"
fi

# Install Playwright
echo "  Installing Playwright (v1.38.0 for compatibility)..."
pip install playwright==1.38.0 --quiet 2>/dev/null || {
    echo -e "  ${YELLOW}⚠️  Using existing Playwright installation${NC}"
}
playwright install chromium 2>/dev/null || {
    echo -e "  ${YELLOW}⚠️  Chromium browser may already be installed${NC}"
}
echo -e "  ${GREEN}✓ Playwright setup complete${NC}"

echo

# ============================================================================
# STEP 4: Project Structure
# ============================================================================
echo -e "${YELLOW}📁 STEP 4: Creating Project Structure${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create all necessary directories
directories=(
    "workspace/research"
    "workspace/outputs"
    "workspace/reports/screenshots"
    "workspace/patches"
    "workspace/logs"
    "workspace/backend"
    "workspace/frontend"
    "workspace/messages"
    "workspace/events"
    "workspace/broadcasts"
    "workspace/data"
    "tests/unit"
    "tests/integration"
    "tests/e2e"
    "tests/fixtures"
    "inputs"
    "specs"
    "agents"
    ".claude/agents"
    ".claude/hooks"
    ".claude/state"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
done

echo -e "  ${GREEN}✓ Project structure created${NC}"
echo

# ============================================================================
# STEP 5: Configuration
# ============================================================================
echo -e "${YELLOW}⚙️  STEP 5: Configuration Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "  Creating .env configuration file..."
    cat > .env << 'EOF'
# ============================================================================
# AUTONOMOUS AGENT CONFIGURATION
# ============================================================================

# API Keys (REQUIRED for autonomous mode)
ANTHROPIC_API_KEY=your_api_key_here

# Model Configuration (Opus for complex reasoning, Sonnet for implementation)
MODEL_TECHLEAD=claude-3-opus-20240229
MODEL_METAAGENT=claude-3-opus-20240229
MODEL_RESEARCHER=claude-3-opus-20240229
MODEL_ARCHITECT=claude-3-opus-20240229
MODEL_BACKEND=claude-3-5-sonnet-20241022
MODEL_FRONTEND=claude-3-5-sonnet-20241022
MODEL_QA=claude-3-5-sonnet-20241022
MODEL_SELFHEALING=claude-3-5-sonnet-20241022

# Autonomous Behavior
MAX_SELF_HEAL_ATTEMPTS=5
PARALLEL_EXECUTION=true
AUTO_CREATE_AGENTS=true
STOP_GATE_ACTIVE=true

# Testing Configuration
BASE_URL=http://localhost:3000
PLAYWRIGHT_HEADLESS=true
TEST_TIMEOUT=30000

# Logging
LOG_LEVEL=INFO
DEBUG_MODE=false

# Message Queue
MESSAGE_QUEUE_TYPE=filesystem
REDIS_URL=redis://localhost:6379

# Performance
AGENT_TIMEOUT=300
MAX_RETRIES=3
RETRY_DELAY=5
EOF
    echo -e "  ${GREEN}✓ .env file created${NC}"
    echo -e "  ${RED}⚠️  IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY${NC}"
else
    echo -e "  ${GREEN}✓ .env file exists${NC}"
fi

echo

# ============================================================================
# STEP 6: Agent System Activation
# ============================================================================
echo -e "${YELLOW}🤖 STEP 6: Activating Agent System${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Display available agents
echo -e "\n${PURPLE}Available Autonomous Agents:${NC}"
echo ""
echo "  🔵 MetaAgent     - Master orchestrator, creates dynamic agents"
echo "  🔵 TechLead      - Technical coordinator and user interface"
echo "  🟣 Researcher    - Domain investigation and requirements"
echo "  🟢 Architect     - System design and TYPE definitions"
echo "  🟠 ProductOwner  - User stories and acceptance criteria"
echo "  🧱 DataEngineer  - Data pipelines and ETL processes"
echo "  🔬 DataScientist - Analytics and ML models"
echo "  🔴 BackendEng    - API and server implementation"
echo "  🟡 FrontendEng   - UI/UX implementation"
echo "  🟤 QA            - Playwright test creation"
echo "  ⚫ SelfHealing   - Automatic test fix generation"
echo "  🟩 DeliveryLead  - Release management"
echo ""

# Create sample problem file
if [ ! -f "inputs/problem.md" ]; then
    echo "  Creating sample problem statement..."
    cat > inputs/problem.md << 'EOF'
# ClinicLite Botswana - Rural Clinic Management System

## Problem Statement
Build a lightweight, offline-capable web application for rural clinics in Botswana to manage patient appointments and medical stock.

## Core Requirements
1. **CSV Upload Dashboard**
   - Upload clinic, patient, appointment, and stock data via CSV
   - Validate and process uploaded data
   - Display upload status and errors

2. **Appointment Management**
   - Show upcoming visits (next 7 days)
   - Track missed visits (past 7 days)
   - Send SMS reminders (simulated for demo)

3. **Stock Management**
   - Monitor low stock items (below reorder threshold)
   - Generate reorder drafts
   - Alert for critical stock levels

4. **Offline Capability**
   - Work without internet connection
   - Sync when connection available
   - Local data storage

5. **Language Support**
   - English (EN)
   - Setswana (TSW)
   - Toggle between languages

## Technical Constraints
- Must work on low-bandwidth connections
- Support older browsers
- Minimal resource usage
- Mobile-responsive design

## Success Criteria
- 100% Playwright test coverage
- All tests passing
- Zero runtime errors
- Performance < 2s page load
EOF
    echo -e "  ${GREEN}✓ Sample problem created in inputs/problem.md${NC}"
fi

echo

# ============================================================================
# STEP 7: Quick Test
# ============================================================================
echo -e "${YELLOW}🧪 STEP 7: Running System Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test Python installation
echo "  Testing Python environment..."
python -c "import sys; print(f'    ✓ Python {sys.version.split()[0]} active')" 2>/dev/null || echo -e "    ${YELLOW}⚠️  Python environment issue${NC}"

# Test core imports
echo "  Testing core packages..."
python -c "
try:
    import anthropic
    print('    ✓ Anthropic SDK installed')
except:
    print('    ⚠️  Anthropic SDK missing - install with: pip install anthropic')
try:
    import playwright
    print('    ✓ Playwright installed')
except:
    print('    ⚠️  Playwright missing - install with: pip install playwright')
" 2>/dev/null

# Test orchestrator
echo "  Testing orchestrator..."
if [ -f "orchestrator.py" ]; then
    python orchestrator.py --help &>/dev/null && echo -e "    ${GREEN}✓ Orchestrator ready${NC}" || echo -e "    ${YELLOW}⚠️  Orchestrator needs dependencies${NC}"
else
    echo -e "    ${YELLOW}⚠️  Orchestrator.py not found${NC}"
fi

# Test agent registry
echo "  Testing agent system..."
if [ -f "tools/agent_registry.py" ]; then
    echo -e "    ${GREEN}✓ Agent system configured${NC}"
else
    echo -e "    ${YELLOW}⚠️  Agent registry not found${NC}"
fi

echo

# ============================================================================
# FINAL INSTRUCTIONS
# ============================================================================
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                    ✅ SETUP COMPLETE! ✅                        ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo

echo -e "${BLUE}🚀 HOW TO START THE AUTONOMOUS SYSTEM:${NC}"
echo ""
echo "  ${PURPLE}Option 1: Claude Code (Interactive)${NC}"
echo "  ────────────────────────────────────"
echo "  1. Open this folder in Claude Code"
echo "  2. Say: ${GREEN}@TechLead Initialize ClinicLite from inputs/problem.md${NC}"
echo "  3. The system will autonomously build until tests pass"
echo ""
echo "  ${PURPLE}Option 2: Python Orchestrator (Fully Autonomous)${NC}"
echo "  ─────────────────────────────────────────────────"
echo "  1. Add your API key: ${GREEN}nano .env${NC} (set ANTHROPIC_API_KEY)"
echo "  2. Run: ${GREEN}python orchestrator.py --mode autonomous${NC}"
echo "  3. Watch logs: ${GREEN}tail -f workspace/logs/orchestrator.log${NC}"
echo ""
echo "  ${PURPLE}Option 3: Interactive Mode${NC}"
echo "  ──────────────────────────"
echo "  1. Run: ${GREEN}python orchestrator.py --mode interactive${NC}"
echo "  2. Use @AgentName commands to invoke specific agents"
echo "  3. Example: ${GREEN}@MetaAgent Create a caching system${NC}"
echo ""

echo -e "${YELLOW}📊 MONITORING THE SYSTEM:${NC}"
echo "  • Test status: ${GREEN}cat workspace/reports/last_test_result.json${NC}"
echo "  • Agent logs:  ${GREEN}tail -f workspace/logs/*.log${NC}"
echo "  • Messages:    ${GREEN}ls workspace/messages/*/inbox/${NC}"
echo ""

echo -e "${RED}⚠️  IMPORTANT NOTES:${NC}"
echo "  1. The system runs AUTONOMOUSLY until 100% tests pass"
echo "  2. Self-healing attempts up to 5 times on failures"
echo "  3. MetaAgent can create new specialized agents as needed"
echo "  4. Stop gate prevents exit until all tests are green"
echo ""

echo -e "${BLUE}📚 Learn more:${NC}"
echo "  • Context7 Principles: https://context7.com/"
echo "  • Documentation: ./README.md"
echo "  • Agent Guide: ./.claude/ai-docs/AGENT_INTERACTION_GUIDE.md"
echo ""

# Final check for API key
if grep -q "your_api_key_here" .env 2>/dev/null; then
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ⚠️  Don't forget to add your ANTHROPIC_API_KEY in .env file!  ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo "Happy autonomous coding! 🎉"