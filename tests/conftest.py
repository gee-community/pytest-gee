"""Pytest session configuration."""

import pytest_gee


def pytest_configure():
    """Init GEE in the test environment."""
    pytest_gee.init_ee_from_token()
