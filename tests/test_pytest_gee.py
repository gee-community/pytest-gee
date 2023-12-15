"""Test the pytest_gee package."""
import ee

import pytest_gee


def test_hash_fixture(gee_hash):
    """Test the hash fixture."""
    assert isinstance(gee_hash, str)
    assert len(gee_hash) == 32


def test_gee_init():
    """Test the init_ee_from_token function."""
    assert ee.Number(1).getInfo() == 1


def test_init_tree(gee_hash, account_root, test_folder):
    """Test the init_tree function."""
    # search all the assets contained in the test_folder
    asset_list = pytest_gee.utils.get_assets(account_root)

    # identify specific files and folders
    folder = test_folder / f"{gee_hash}_folder"
    image = folder / f"{gee_hash}_image"
    feature_collection = folder / f"{gee_hash}_fc"

    # check that they exist
    assert str(test_folder) in asset_list
    assert str(folder) in asset_list
    assert str(image) in asset_list
    assert str(feature_collection) in asset_list
