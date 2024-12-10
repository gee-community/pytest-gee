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


def test_list_regression(list_regression):
    """Test the list_regression fixture."""
    data = ee.List([1, 2, 3])
    list_regression.check(data)


def test_list_regression_prescision(list_regression):
    """Test the list_regression fixture with a different precision."""
    data = ee.List([1.123456789, 2.123456789, 3.123456789])
    list_regression.check(data, prescision=3)

    
def test_feature_collection_regression(feature_collection_regression):
    """Test the feature_collection_regression fixture."""
    fc = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq("ADM0_NAME", "Holy See"))
    feature_collection_regression.check(fc)

    
def test_dictionary_regression(dictionary_regression):
    """Test the dictionary_regression fixture."""
    data = ee.Dictionary({"a": 1, "b": 2})
    dictionary_regression.check(data)


def test_dictionary_regression_prescision(dictionary_regression):
    """Test the dictionary_regression fixture with a different precision."""
    data = ee.Dictionary({"a": 1.123456789, "b": 2.123456789})
    dictionary_regression.check(data, prescision=3)
