"""Pytest session configuration."""

import os

import ee
import pytest

import pytest_gee


def pytest_configure():
    """Init GEE in the test environment."""
    if os.getenv("EARTHENGINE_SERVICE_ACCOUNT"):
        pytest_gee.init_ee_from_service_account()

    pytest_gee.init_ee_from_token()


@pytest.fixture(scope="session")
def gee_folder_structure():
    """Override the default test folder structure."""
    point = ee.Geometry.Point([0, 0])
    return {
        "folder": {
            "image": ee.Image(1).clipToBoundsAndScale(point.buffer(100), scale=30),
            "fc": ee.FeatureCollection(point),
        }
    }
