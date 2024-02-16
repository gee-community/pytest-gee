"""Test the pytest_gee package."""

import json
import os
from pathlib import Path

import ee
import pytest

import pytest_gee


def test_hash_fixture(gee_hash):
    """Test the hash fixture."""
    assert isinstance(gee_hash, str)
    assert len(gee_hash) == 32


def test_gee_init_from_token():
    """Test the init_ee_from_token function."""
    credentials_filepath = Path(ee.oauth.get_credentials_path())
    existing = False

    try:
        # Reset credentials to force the initialization
        # It can be initiated from different imports
        ee.data._credentials = None

        # Get the credentials path

        # Remove the credentials file if it exists
        if credentials_filepath.exists():
            existing = True
            credentials_filepath.rename(credentials_filepath.with_suffix(".json.bak"))

        # Act: Earthengine token should be created
        pytest_gee.init_ee_from_token()

        assert credentials_filepath.exists()

        # read the back up and remove the "project_id" key
        credentials = json.loads(credentials_filepath.with_suffix(".json.bak").read_text())

        ## 2. Assert when there's no a project associated
        # remove the project_id key if it exists
        credentials.pop("project_id", None)
        credentials.pop("project", None)
        if "EARTHENGINE_PROJECT" in os.environ:
            del os.environ["EARTHENGINE_PROJECT"]

        # write the new credentials
        credentials_filepath.write_text(json.dumps(credentials))

        with pytest.raises(NameError) as e:
            pytest_gee.init_ee_from_token()

        # Access the exception message via `e.value`
        error_message = str(e.value)
        assert "The project name cannot be detected" in error_message

    finally:
        # restore the file
        if existing:
            credentials_filepath.with_suffix(".json.bak").rename(credentials_filepath)

        # check that no error is raised
        pytest_gee.init_ee_from_token()


def test_gee_init():
    """Test the init_ee_from_token function."""
    assert ee.Number(1).getInfo() == 1


def test_structure(gee_folder_structure):
    """Test the structure fixture."""
    assert isinstance(gee_folder_structure, dict)
    assert "folder" in gee_folder_structure
    assert "image" in gee_folder_structure["folder"]
    assert "fc" in gee_folder_structure["folder"]


def test_init_tree(gee_folder_root, gee_test_folder):
    """Test the init_tree function."""
    # search all the assets contained in the test_folder
    asset_list = pytest_gee.utils.get_assets(gee_folder_root)
    asset_list = [i["name"] for i in asset_list]

    # identify specific files and folders
    folder = gee_test_folder / "folder"
    image = folder / "image"
    feature_collection = folder / "fc"

    # check that they exist
    assert str(gee_test_folder) in asset_list
    assert str(folder) in asset_list
    assert str(image) in asset_list
    assert str(feature_collection) in asset_list
