"""Pytest session configuration."""
import ee
import pytest

import pytest_gee


def pytest_configure():
    """Init GEE in the test environment."""
    pytest_gee.init_ee_from_token()


@pytest.fixture(scope="session")
def test_folder(gee_hash, account_root):
    """Create a test folder for the test session."""
    point = ee.Geometry.Point([0, 0])
    structure = {
        "folder": {
            "image": ee.Image(1).clipToBoundsAndScale(point.buffer(100), scale=30),
            "fc": ee.FeatureCollection(point),
        }
    }
    folder = pytest_gee.init_tree(structure, gee_hash, account_root)

    yield folder

    pytest_gee.delete_assets(folder, False)
