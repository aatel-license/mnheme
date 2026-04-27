"""
conftest.py — pytest configuration for MNHEME test suite.
Adds project root to sys.path so imports work from tests/.
"""
import sys, pathlib

# Add project root (parent of tests/)
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
