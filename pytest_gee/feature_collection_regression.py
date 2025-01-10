"""Implementation of the ``feature_collection_regression`` fixture."""

import os
from typing import Optional

import ee
import geopandas as gpd
from pytest_regressions.data_regression import DataRegressionFixture

from .utils import round_data


class FeatureCollectionFixture(DataRegressionFixture):
    """Fixture for regression testing of :py:class:`ee.FeatureCollection`."""

    def check(
        self,
        data_fc: ee.FeatureCollection,
        basename: Optional[str] = None,
        fullpath: Optional[os.PathLike] = None,
        prescision: int = 6,
        drop_index=False,
    ):
        """Check the given list against a previously recorded version, or generate a new file.

        Parameters:
            data_fc: The feature collection to check.
            basename: The basename of the file to test/record. If not given the name of the test is used.
            fullpath: complete path to use as a reference file. This option will ignore ``datadir`` fixture when reading *expected* files but will still use it to write *obtained* files. Useful if a reference file is located in the session data dir for example.
            precision: The number of decimal places to round to when comparing floats.
            drop_index: If True, the ``system:index`` property will be removed from the feature collection before checking.
        """
        if drop_index is True:
            data_fc = data_fc.map(lambda f: f.select(f.propertyNames().remove("system:index")))

        # round the geometry using geopandas to make sre with use the specific number of decimal places
        gdf = gpd.GeoDataFrame.from_features(data_fc.getInfo())
        gdf.geometry = gdf.set_precision(grid_size=10 ** (-prescision)).remove_repeated_points()

        # round any float value before serving the data to the check function
        data = gdf.to_geo_dict()
        data = round_data(data, prescision)

        super().check(data, basename=basename, fullpath=fullpath)
