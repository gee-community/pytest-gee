"""Implementation of the ``feature_collection_regression`` fixture."""

import os
from typing import Optional

import ee
import geopandas as gpd
from pytest_regressions.data_regression import DataRegressionFixture

from .utils import build_fullpath, check_serialized, round_data


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

        # build the different filename to be consistent between our 3 checks
        data_name = build_fullpath(
            datadir=self.original_datadir,
            request=self.request,
            extension=".yml",
            basename=basename,
            fullpath=fullpath,
            with_test_class_names=self.with_test_class_names,
        )

        serialized_name = data_name.with_stem(f"serialized_{data_name.stem}").with_suffix(".yml")

        is_serialized_equal = check_serialized(
            object=data_fc,
            path=serialized_name,
            datadir=self.datadir,
            request=self.request,
        )

        if is_serialized_equal:
            # serialized is equal? -> pass test
            # TODO: add proper logging
            return
        else:
            # round the geometry using geopandas to make sre with use the specific number of decimal places
            gdf = gpd.GeoDataFrame.from_features(data_fc.getInfo())
            gdf.geometry = gdf.set_precision(grid_size=10 ** (-prescision)).remove_repeated_points()

            # round any float value before serving the data to the check function
            data = gdf.to_geo_dict()
            data = round_data(data, prescision)

            super().check(data, fullpath=data_name)

            # if we are here it means that the query result is equal but the serialized is not -> regenerate serialized
            serialized_name.unlink(missing_ok=True)
            check_serialized(
                object=data_fc,
                path=serialized_name,
                datadir=self.datadir,
                request=self.request,
            )
