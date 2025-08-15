"""
Codegen SDK Test Suite

This module contains comprehensive tests for the Codegen SDK including:
- Unit tests for all components
- Integration tests with real API calls
- Performance and caching tests
- Agent run lifecycle validation
- State management pattern analysis
"""

# Test configuration
import os

# Default test configuration
TEST_CONFIG = {
    "CODEGEN_ORG_ID": int(os.getenv("CODEGEN_ORG_ID", "323")),
    "CODEGEN_API_TOKEN": os.getenv("CODEGEN_API_TOKEN", ""),
    "BASE_URL": "https://api.codegen.com/v1",
    "POLL_INTERVAL": 1.0,
    "MAX_WAIT_TIME": 300,
    "LOG_BATCH_SIZE": 100,
}

__version__ = "2.0.0"
__all__ = ["TEST_CONFIG"]

