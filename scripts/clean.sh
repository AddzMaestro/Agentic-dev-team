#!/usr/bin/env bash
# Project Cleaner Script
# Removes unnecessary files while preserving critical components
# Following Context7 principles - https://context7.com/

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Zero-Error Project Cleaner${NC}"
echo "=================================="
echo ""

# Track what we're cleaning
TOTAL_BEFORE=$(du -sh . 2>/dev/null | cut -f1)
FILES_REMOVED=0
DIRS_REMOVED=0

# Function to safely remove files/directories
safe_remove() {
    local path=$1
    local type=$2  # "file" or "dir"
    
    if [ -e "$path" ]; then
        if [ "$type" = "dir" ]; then
            if [ -d "$path" ]; then
                rm -rf "$path"
                ((DIRS_REMOVED++))
                echo -e "${GREEN}✓${NC} Removed directory: $path"
            fi
        else
            if [ -f "$path" ]; then
                rm -f "$path"
                ((FILES_REMOVED++))
                echo -e "${GREEN}✓${NC} Removed file: $path"
            fi
        fi
    fi
}

# Function to clean pattern with find
clean_pattern() {
    local pattern=$1
    local message=$2
    
    echo -e "${YELLOW}Cleaning${NC} $message..."
    
    while IFS= read -r -d '' file; do
        safe_remove "$file" "file"
    done < <(find . -type f -name "$pattern" -print0 2>/dev/null)
}

# Parse command line arguments
DEEP_CLEAN=false
KEEP_WORKSPACE=false
KEEP_VENV=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --deep)
            DEEP_CLEAN=true
            shift
            ;;
        --keep-workspace)
            KEEP_WORKSPACE=true
            shift
            ;;
        --keep-venv)
            KEEP_VENV=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            echo -e "${YELLOW}DRY RUN MODE - No files will be deleted${NC}"
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --deep           Deep clean including workspace and test results"
            echo "  --keep-workspace Keep workspace directory contents"
            echo "  --keep-venv      Keep virtual environment"
            echo "  --dry-run        Show what would be deleted without removing"
            echo "  --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Standard clean"
            echo "  $0 --deep             # Deep clean everything"
            echo "  $0 --keep-workspace   # Clean but preserve workspace"
            echo "  $0 --dry-run          # Preview what will be cleaned"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# If dry run, override the safe_remove function
if [ "$DRY_RUN" = true ]; then
    safe_remove() {
        local path=$1
        local type=$2
        if [ -e "$path" ]; then
            echo -e "${BLUE}[DRY RUN]${NC} Would remove: $path"
        fi
    }
fi

echo -e "${YELLOW}Starting cleanup...${NC}"
echo ""

# ============================================================================
# 1. Python Cache and Compiled Files
# ============================================================================
echo -e "${BLUE}[1/10] Python artifacts${NC}"
clean_pattern "*.pyc" "Python compiled files"
clean_pattern "*.pyo" "Python optimized files"
clean_pattern "*.pyd" "Python extension modules"
safe_remove "__pycache__" "dir"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Python build artifacts
safe_remove "build" "dir"
safe_remove "dist" "dir"
safe_remove "*.egg-info" "dir"
safe_remove ".eggs" "dir"
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# ============================================================================
# 2. Testing Artifacts
# ============================================================================
echo ""
echo -e "${BLUE}[2/10] Testing artifacts${NC}"
safe_remove ".pytest_cache" "dir"
safe_remove ".coverage" "file"
safe_remove "coverage.xml" "file"
safe_remove "htmlcov" "dir"
safe_remove ".hypothesis" "dir"
safe_remove ".tox" "dir"
safe_remove ".nox" "dir"
clean_pattern "*.coverage" "Coverage files"
clean_pattern ".coverage.*" "Coverage data files"

# Playwright test results (unless keeping workspace)
if [ "$KEEP_WORKSPACE" = false ]; then
    safe_remove "test-results" "dir"
    safe_remove "playwright-report" "dir"
    safe_remove "tests/e2e/screenshots" "dir"
    safe_remove "tests/e2e/videos" "dir"
    safe_remove "tests/e2e/traces" "dir"
fi

# ============================================================================
# 3. Type Checking and Linting
# ============================================================================
echo ""
echo -e "${BLUE}[3/10] Type checking and linting${NC}"
safe_remove ".mypy_cache" "dir"
safe_remove ".dmypy.json" "file"
safe_remove "dmypy.json" "file"
safe_remove ".ruff_cache" "dir"
safe_remove ".pylint.d" "dir"
clean_pattern ".eslintcache" "ESLint cache"

# ============================================================================
# 4. Node.js Artifacts (if deep clean)
# ============================================================================
echo ""
echo -e "${BLUE}[4/10] Node.js artifacts${NC}"
if [ "$DEEP_CLEAN" = true ]; then
    safe_remove "node_modules" "dir"
    echo -e "${YELLOW}Note: Run 'npm install' to restore Node dependencies${NC}"
fi
clean_pattern "npm-debug.log*" "npm debug logs"
clean_pattern "yarn-debug.log*" "yarn debug logs"
clean_pattern "yarn-error.log*" "yarn error logs"
clean_pattern "lerna-debug.log*" "lerna debug logs"
safe_remove ".npm" "dir"

# ============================================================================
# 5. Virtual Environments (if not keeping)
# ============================================================================
echo ""
echo -e "${BLUE}[5/10] Virtual environments${NC}"
if [ "$KEEP_VENV" = false ]; then
    safe_remove ".venv" "dir"
    safe_remove "venv" "dir"
    safe_remove "env" "dir"
    safe_remove "ENV" "dir"
    if [ "$DEEP_CLEAN" = true ]; then
        echo -e "${YELLOW}Note: Run './scripts/bootstrap.sh' to recreate virtual environment${NC}"
    fi
fi

# ============================================================================
# 6. Workspace Cleanup (configurable)
# ============================================================================
echo ""
echo -e "${BLUE}[6/10] Workspace cleanup${NC}"
if [ "$KEEP_WORKSPACE" = false ] && [ "$DEEP_CLEAN" = true ]; then
    # Clean workspace but preserve structure
    find workspace/logs -type f -name "*.log" -delete 2>/dev/null || true
    find workspace/reports -type f \( -name "*.html" -o -name "*.xml" -o -name "*.json" \) -delete 2>/dev/null || true
    find workspace/messages -type f -delete 2>/dev/null || true
    find workspace/events -type f -delete 2>/dev/null || true
    find workspace/broadcasts -type f -delete 2>/dev/null || true
    find workspace/patches -type f -delete 2>/dev/null || true
    
    # Clean generated outputs
    safe_remove "workspace/outputs/architecture.md" "file"
    safe_remove "workspace/outputs/backlog.md" "file"
    safe_remove "workspace/outputs/data_eng.md" "file"
    safe_remove "workspace/outputs/data_sci.md" "file"
    safe_remove "workspace/research/summary.md" "file"
    safe_remove "workspace/research/sources.md" "file"
    
    echo -e "${GREEN}✓${NC} Workspace cleaned while preserving structure"
elif [ "$KEEP_WORKSPACE" = true ]; then
    echo -e "${YELLOW}Skipping workspace (--keep-workspace flag)${NC}"
fi

# ============================================================================
# 7. Temporary and Backup Files
# ============================================================================
echo ""
echo -e "${BLUE}[7/10] Temporary and backup files${NC}"
clean_pattern "*.tmp" "Temporary files"
clean_pattern "*.temp" "Temp files"
clean_pattern "*.bak" "Backup files"
clean_pattern "*.backup" "Backup files"
clean_pattern "*.old" "Old files"
clean_pattern "*.orig" "Original files"
clean_pattern "*.swp" "Vim swap files"
clean_pattern "*.swo" "Vim swap files"
clean_pattern "*~" "Editor backup files"
clean_pattern ".DS_Store" "macOS metadata"
clean_pattern "Thumbs.db" "Windows thumbnails"

# ============================================================================
# 8. IDE and Editor Files
# ============================================================================
echo ""
echo -e "${BLUE}[8/10] IDE and editor files${NC}"
safe_remove ".idea" "dir"
safe_remove ".vscode" "dir"
clean_pattern "*.iml" "IntelliJ module files"
clean_pattern "*.ipr" "IntelliJ project files"
clean_pattern "*.iws" "IntelliJ workspace files"
clean_pattern ".project" "Eclipse project files"
clean_pattern ".classpath" "Eclipse classpath"

# ============================================================================
# 9. Log Files
# ============================================================================
echo ""
echo -e "${BLUE}[9/10] Log files${NC}"
clean_pattern "*.log" "Log files"
clean_pattern "*.log.*" "Rotated log files"
safe_remove "logs" "dir"

# ============================================================================
# 10. Project-Specific Cleanup
# ============================================================================
echo ""
echo -e "${BLUE}[10/10] Project-specific cleanup${NC}"

# ClinicLite specific files
safe_remove "messages_outbox.csv" "file"
safe_remove "reorder_draft.csv" "file"
clean_pattern "uploaded_*.csv" "Uploaded CSV files"

# Generated specs (preserve template)
safe_remove "specs/PRIMARY_SPEC.md" "file"

# Temporary project directories
safe_remove "hello-world" "dir"
safe_remove "zero-error-template" "dir"

# Database files
clean_pattern "*.db" "Database files"
clean_pattern "*.sqlite" "SQLite files"
clean_pattern "*.sqlite3" "SQLite3 files"

# Archive files (optional)
if [ "$DEEP_CLEAN" = true ]; then
    clean_pattern "*.zip" "ZIP archives"
    clean_pattern "*.tar.gz" "Tar archives"
    clean_pattern "*.rar" "RAR archives"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "=================================="
echo -e "${GREEN}✅ Cleanup Complete!${NC}"
echo ""

# Calculate space saved
TOTAL_AFTER=$(du -sh . 2>/dev/null | cut -f1)

echo "Summary:"
echo "  Files removed: $FILES_REMOVED"
echo "  Directories removed: $DIRS_REMOVED"
echo "  Size before: $TOTAL_BEFORE"
echo "  Size after: $TOTAL_AFTER"
echo ""

# Provide next steps based on what was cleaned
if [ "$DEEP_CLEAN" = true ]; then
    echo -e "${YELLOW}Next steps after deep clean:${NC}"
    if [ "$KEEP_VENV" = false ]; then
        echo "  1. Run: ./scripts/bootstrap.sh  # Recreate virtual environment"
    fi
    echo "  2. Run: npm install              # Restore Node.js dependencies"
    echo "  3. Run: playwright install        # Reinstall browsers"
fi

# Check if critical files are still present
echo ""
echo -e "${BLUE}Critical files check:${NC}"

critical_files=(
    "orchestrator.py"
    "pyproject.toml"
    "requirements.txt"
    "README.md"
    "CLAUDE.md"
    ".gitignore"
    "scripts/bootstrap.sh"
    "scripts/ci.sh"
    "scripts/clean.sh"
)

all_present=true
for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (missing)"
        all_present=false
    fi
done

if [ "$all_present" = true ]; then
    echo -e "${GREEN}All critical files present!${NC}"
else
    echo -e "${RED}Warning: Some critical files are missing${NC}"
fi

echo ""
echo "Done! Your project is clean and organized."