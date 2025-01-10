"""Test the pytest_gee package."""

import ee

import pytest_gee

landsat_image = "LANDSAT/LC08/C02/T1_L2/LC08_191031_20240607"
"landsat image from 2024-06-07 on top of Rome"


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


def test_list_regression(ee_list_regression):
    """Test the ee_list_regression fixture."""
    data = ee.List([1, 2, 3])
    ee_list_regression.check(data)


def test_list_regression_prescision(ee_list_regression):
    """Test the ee_list_regression fixture with a different precision."""
    data = ee.List([1.123456789, 2.123456789, 3.123456789])
    ee_list_regression.check(data, prescision=3)


def test_feature_collection_regression(ee_feature_collection_regression):
    """Test the ee_feature_collection_regression fixture."""
    fc = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq("ADM0_NAME", "Holy See"))
    ee_feature_collection_regression.check(fc)


def test_feature_collection_regression_prescision(ee_feature_collection_regression):
    """Test the ee_feature_collection_regression fixture."""
    fc = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq("ADM0_NAME", "Holy See"))
    ee_feature_collection_regression.check(fc, prescision=4)


def test_feature_collection_regression_no_index(ee_feature_collection_regression):
    """Test the ee_feature_collection_regression fixture."""
    point = ee.Geometry.Point([0, 0])
    size = ee.List.sequence(50, 100, 10)
    geometries = size.map(lambda s: point.buffer(s, ee.Number(s).divide(5)))
    fc = ee.FeatureCollection(geometries.map(lambda g: ee.Feature(ee.Geometry(g))))
    ee_feature_collection_regression.check(fc, drop_index=True, prescision=4)


def test_dictionary_regression(ee_dictionary_regression):
    """Test the ee_dictionary_regression fixture."""
    data = ee.Dictionary({"a": 1, "b": 2})
    ee_dictionary_regression.check(data)


def test_dictionary_regression_prescision(ee_dictionary_regression):
    """Test the ee_dictionary_regression fixture with a different precision."""
    data = ee.Dictionary({"a": 1.123456789, "b": 2.123456789})
    ee_dictionary_regression.check(data, prescision=3)


def test_image_regression_3_bands(ee_image_regression):
    """Test the image_regression fixture."""
    image = ee.Image(landsat_image).select(["SR_B4", "SR_B3", "SR_B2"])
    ee_image_regression.check(image, scale=1000)


def test_image_regression_1_band(ee_image_regression):
    """Test the image_regression fixture."""
    image = ee.Image(landsat_image).normalizedDifference(["SR_B5", "SR_B4"])
    ee_image_regression.check(image, scale=1000)


def test_image_regression_with_viz(ee_image_regression):
    """Test the image_regression fixture."""
    image = ee.Image(landsat_image).normalizedDifference(["SR_B5", "SR_B4"])
    # use magma palette and stretched to 2 sigma
    palette = ["#000004", "#2C105C", "#711F81", "#B63679", "#EE605E", "#FDAE78", "#FCFDBF"]
    viz = {"bands": ["nd"], "min": 0.0122, "max": 1.237, "palette": palette}
    ee_image_regression.check(image, scale=1000, viz_params=viz)
