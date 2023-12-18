"""A pytest plugin to build a GEE environment for a test session."""
from __future__ import annotations

import uuid
from pathlib import PurePosixPath

import ee
import pytest

from . import utils


@pytest.fixture(scope="session")
def gee_hash():
    """Generate a unique hash for the test session."""
    return uuid.uuid4().hex


@pytest.fixture(scope="session")
def gee_folder_root():
    """Link to the root folder of the connected account."""
    return PurePosixPath(ee.data.getAssetRoots()[0]["id"])


@pytest.fixture(scope="session")
def gee_folder_structure():
    """The structure of the generated test folder."""
    return {}


@pytest.fixture(scope="session")
def gee_test_folder(gee_hash, gee_folder_root, gee_folder_structure):
    """Create a test folder for the duration of the test session."""
    folder = utils.init_tree(gee_folder_structure, gee_hash, gee_folder_root)

    yield folder

    utils.delete_assets(folder, False)
