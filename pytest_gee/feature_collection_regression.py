"""Implementation of the ``feature_collection_regression`` fixture."""

import os
from contextlib import suppress
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

        # check the previously registered serialized call from GEE. If it matches the current call,
        # we don't need to check the data
        with suppress(BaseException):
            check_serialized(
                object=data_fc,
                path=serialized_name,
                datadir=self.datadir,
                original_datadir=self.original_datadir,
                request=self.request,
                with_test_class_names=self.with_test_class_names,
            )
            return

        # delete the previously created file if wasn't successful
        serialized_name.unlink(missing_ok=True)

        # round the geometry using geopandas to make sre with use the specific number of decimal places
        gdf = gpd.GeoDataFrame.from_features(data_fc.getInfo())
        gdf.geometry = gdf.set_precision(grid_size=10 ** (-prescision)).remove_repeated_points()

        # round any float value before serving the data to the check function
        data = gdf.to_geo_dict()
        data = round_data(data, prescision)

        # if it needs to be checked, we need to round the float values to the same precision as the
        # reference file
        try:
            super().check(data, fullpath=data_name)

            # IF we are here it means the data has been modified so we edit the API call accordingly
            # to make sure next run will not be forced to call the API for a response.
            with suppress(BaseException):
                check_serialized(
                    object=data_fc,
                    path=data_name,
                    datadir=self.datadir,
                    original_datadir=self.original_datadir,
                    request=self.request,
                    with_test_class_names=self.with_test_class_names,
                    force_regen=True,
                )

        except BaseException as e:
            raise e
