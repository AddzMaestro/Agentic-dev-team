#!/usr/bin/env bash
# Quick Clean Script
# Removes only safe-to-delete files, preserving workspace and environment

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Quick Clean${NC}"
echo "==============="
echo "Removing Python cache, logs, and temporary files..."
echo ""

# Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Test artifacts
rm -rf .pytest_cache 2>/dev/null || true
rm -f .coverage coverage.xml 2>/dev/null || true

# Logs (but not in workspace)
find . -maxdepth 1 -name "*.log" -delete 2>/dev/null || true

# Temporary files
find . -name "*.tmp" -o -name "*.temp" -o -name "*.swp" -o -name "*~" | xargs rm -f 2>/dev/null || true

# OS-specific
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

echo -e "${GREEN}✅ Quick clean complete!${NC}"
echo ""
echo "For deeper cleaning options, run:"
echo "  ./scripts/clean.sh --help"