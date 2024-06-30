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


def test_structure(gee_folder_structure):
    """Test the structure fixture."""
    assert isinstance(gee_folder_structure, dict)
    assert "folder::Folder" in gee_folder_structure
    assert "image" in gee_folder_structure["folder::Folder"]
    assert "fc" in gee_folder_structure["folder::Folder"]
    assert "ic::ImageCollection" in gee_folder_structure
    assert "image1" in gee_folder_structure["ic::ImageCollection"]
    assert "image2" in gee_folder_structure["ic::ImageCollection"]


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
