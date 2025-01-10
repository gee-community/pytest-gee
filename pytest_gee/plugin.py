"""A pytest plugin to build a GEE environment for a test session."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import ee
import pytest

from . import utils
from .dictionary_regression import DictionaryFixture
from .feature_collection_regression import FeatureCollectionFixture
from .image_regression import ImageFixture
from .list_regression import ListFixture


@pytest.fixture(scope="session")
def gee_hash():
    """Generate a unique hash for the test session."""
    return uuid.uuid4().hex


@pytest.fixture(scope="session")
def gee_folder_root():
    """Link to the root folder of the connected account."""
    # The credential information cannot be reached from
    # the ee API as reported in https://issuetracker.google.com/issues/325020447
    project_id = os.environ.get("EARTHENGINE_PROJECT", ee.data._cloud_api_user_project)
    if project_id is None:
        raise ValueError(
            "The project name cannot be detected."
            "Please set the EARTHENGINE_PROJECT environment variable."
        )
    return Path(f"projects/{project_id}/assets")


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


@pytest.fixture
def ee_list_regression(
    datadir: Path, original_datadir: Path, request: pytest.FixtureRequest
) -> ListFixture:
    """Fixture to test :py:class:`ee.List` objects.

    Args:
        datadir: The directory where the data files are stored.
        original_datadir: The original data directory.
        request: The pytest request object.

    Returns:
        The ListFixture object.

    Example:
        .. code-block:: python

            def test_list_regression(list_regression):
                data = ee.List([1, 2, 3])
                list_regression.check(data)
    """
    return ListFixture(datadir, original_datadir, request)


@pytest.fixture
def ee_feature_collection_regression(
    datadir: Path, original_datadir: Path, request: pytest.FixtureRequest
) -> FeatureCollectionFixture:
    """Fixture to test :py:class:`ee.FeatureCollection` objects.

    Args:
        datadir: The directory where the data files are stored.
        original_datadir: The original data directory.
        request: The pytest request object.

    Returns:
        The FeatureCollectionFixture object.

    Example:
        .. code-block:: python

            def test_feature_collection_regression(feature_collection_regression):
                data = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq("ADM0_NAME", "Holy See"))
                feature_collection_regression.check(data)
    """
    return FeatureCollectionFixture(datadir, original_datadir, request)


@pytest.fixture
def ee_dictionary_regression(
    datadir: Path, original_datadir: Path, request: pytest.FixtureRequest
) -> DictionaryFixture:
    """Fixture to test `ee.Dictionary` objects.

    Args:
        datadir: The directory where the data files are stored.
        original_datadir: The original data directory.
        request: The pytest request object.

    Returns:
        The DictionaryFixture object.

    Example:
        .. code-block:: python

            def test_dictionary_regression(dictionary_regression):
                data = ee.Dictionary({"a": 1, "b": 2})
                dictionary_regression.check(data)
    """
    return DictionaryFixture(datadir, original_datadir, request)


@pytest.fixture
def ee_image_regression(
    datadir: Path, original_datadir: Path, request: pytest.FixtureRequest
) -> ImageFixture:
    """Fixture to test :py:class:`ee.Image` objects.

    Args:
        datadir: The directory where the data files are stored.
        original_datadir: The original data directory.
        request: The pytest request object.

    Returns:
        The ImageFixture object.

    Example:
        .. code-block:: python

            def test_image_regression(image_regression):
                data = ee.Image("LANDSAT/LC08/C02/T1_L2/LC08_191031_20210514")
                image_regression.check(data, scale=1000)
    """
    return ImageFixture(datadir, original_datadir, request)
