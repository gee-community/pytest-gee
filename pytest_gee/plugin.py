"""A pytest plugin to build a GEE environment for a test session."""
from __future__ import annotations

import uuid

import ee
import pytest


@pytest.fixture(scope="session")
def gee_hash():
    """Generate a unique hash for the test session."""
    return uuid.uuid4().hex


@pytest.fixture(scope="session")
def account_root():
    """Link to the root folder of the connected account."""
    return ee.data.getAssetRoots()[0]["id"]
