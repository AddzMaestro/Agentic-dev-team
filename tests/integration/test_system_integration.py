"""
Integration tests for system components
"""
import pytest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def test_project_structure():
    """Test that required project files exist"""
    project_root = Path(__file__).parent.parent.parent
    
    required_files = [
        "orchestrator.py",
        "README.md", 
        "requirements.txt",
        ".gitignore",
        "CLAUDE.md"
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"Required file missing: {file_path}"


def test_workspace_directories():
    """Test that workspace directories can be created"""
    project_root = Path(__file__).parent.parent.parent
    workspace_dir = project_root / "workspace"
    
    # Create test directories if they don't exist
    test_dirs = [
        "logs", "reports", "outputs", "patches", 
        "messages", "broadcasts", "data"
    ]
    
    for dir_name in test_dirs:
        dir_path = workspace_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        assert dir_path.exists(), f"Could not create workspace directory: {dir_name}"


def test_agent_configuration():
    """Test that agent configurations are readable"""
    project_root = Path(__file__).parent.parent.parent
    agents_dir = project_root / ".claude" / "agents"
    
    if agents_dir.exists():
        agent_files = list(agents_dir.glob("*.md"))
        assert len(agent_files) > 0, "No agent configuration files found"
        
        # Check that at least one agent file is readable
        for agent_file in agent_files[:3]:  # Check first 3 files
            content = agent_file.read_text()
            assert len(content) > 0, f"Agent file is empty: {agent_file.name}"


def test_environment_setup():
    """Test environment and dependency availability"""
    # Check Python version
    import sys
    assert sys.version_info >= (3, 8), "Python 3.8+ required"
    
    # Check core dependencies
    try:
        import anthropic
        import pydantic
        import playwright
        import pytest
    except ImportError as e:
        pytest.fail(f"Core dependency missing: {e}")


if __name__ == "__main__":
    pytest.main([__file__])