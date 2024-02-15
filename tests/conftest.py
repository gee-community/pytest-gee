"""Pytest session configuration."""
import os
from pathlib import Path

import ee
import pytest

import pytest_gee


def pytest_configure():
    """Init GEE in the test environment."""
    pytest_gee.init_ee_from_service_account()


# this fixture need override at the moment as the credential information cannot be reached from
# the ee API as reported in https://issuetracker.google.com/issues/325020447
@pytest.fixture(scope="session")
def gee_folder_root():
    """Link to the root folder of the connected account."""
    project_id = os.environ.get("EARTHENGINE_PROJECT", ee.data._cloud_api_user_project)
    if project_id is None:
        raise ValueError(
            "The project name cannot be detected."
            "Please set the EARTHENGINE_PROJECT environment variable."
        )
    return Path(f"projects/{project_id}/assets")


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
