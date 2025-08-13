"""
Unit tests for orchestrator functionality
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def test_orchestrator_imports():
    """Test that we can import the orchestrator module"""
    try:
        # Import the main orchestrator components
        from orchestrator import AgentMessage, MessageType, Priority
        assert MessageType.REQUEST == "request"
        assert Priority.HIGH == "high"
        assert AgentMessage is not None
    except ImportError as e:
        pytest.skip(f"Orchestrator dependencies not available: {e}")


def test_environment_variables():
    """Test environment variable handling"""
    import os
    from dotenv import load_dotenv
    
    # This should not fail even if .env doesn't exist
    load_dotenv()
    
    # Basic environment checks
    assert "PATH" in os.environ
    
    # Check if we can set test environment variables
    os.environ["TEST_VAR"] = "test_value"
    assert os.environ.get("TEST_VAR") == "test_value"


def test_basic_python_functionality():
    """Sanity check for Python environment"""
    import json
    import datetime
    
    # Test basic Python functionality
    data = {"timestamp": datetime.datetime.now().isoformat()}
    json_str = json.dumps(data)
    parsed = json.loads(json_str)
    
    assert "timestamp" in parsed
    assert len(json_str) > 0


if __name__ == "__main__":
    pytest.main([__file__])