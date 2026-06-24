"""
Pytest configuration for test suite.
Database initialization is handled by FastAPI's lifespan context manager.
"""

import pytest


# Pytest configuration - no fixtures needed
# The app's lifespan in main.py handles database init/close when AsyncClient is created