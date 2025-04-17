import os
import sys
import pytest

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_environment():
    """Test that the environment is set up correctly"""
    # This is a basic test that doesn't actually test functionality
    # but ensures the test framework is working
    assert True

def test_python_version():
    """Test that the Python version is correct"""
    assert sys.version_info.major == 3
    # Allow Python 3.9 or higher
    assert sys.version_info.minor >= 9

def test_imports():
    """Test that key modules can be imported"""
    # Try importing key modules
    import pandas as pd
    import numpy as np
    import sklearn
    import fastapi

    # Verify module versions
    assert pd.__version__ is not None
    assert np.__version__ is not None
    assert sklearn.__version__ is not None
    assert fastapi.__version__ is not None
