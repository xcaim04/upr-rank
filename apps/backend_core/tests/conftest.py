"""Shared pytest configuration for the backend tests."""

import sys
from pathlib import Path

# Make the backend src package importable when running tests from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
