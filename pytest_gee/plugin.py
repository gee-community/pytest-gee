"""A pytest plugin to build a GEE environment for a test session."""
import uuid

import pytest


@pytest.fixture(scope="session")
def gee_hash():
    """Generate a unique hash for the test session."""
    return uuid.uuid4().hex
