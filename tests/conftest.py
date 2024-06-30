"""Pytest session configuration."""

import ee
import pytest

import pytest_gee


def pytest_configure():
    """Init GEE in the test environment."""
    pytest_gee.init_ee_from_service_account()


@pytest.fixture(scope="session")
def gee_folder_structure():
    """Override the default test folder structure."""
    point = ee.Geometry.Point([0, 0])
    return {
        "folder::Folder": {
            "image": ee.Image(1).clipToBoundsAndScale(point.buffer(100), scale=30),
            "fc": ee.FeatureCollection(point),
        },
        "ic::ImageCollection": {
            "image1": ee.Image(1).clipToBoundsAndScale(point.buffer(100), scale=30),
            "image2": ee.Image(1).clipToBoundsAndScale(point.buffer(100), scale=30),
        },
    }
