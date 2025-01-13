"""Implementation of the ``list_regression`` fixture."""

import os
from contextlib import suppress
from typing import Optional

import ee
from pytest_regressions.data_regression import DataRegressionFixture

from .utils import build_fullpath, check_serialized, round_data


class ListFixture(DataRegressionFixture):
    """Fixture for regression testing of :py:class:`ee.List`."""

    def check(
        self,
        data_list: ee.List,
        basename: Optional[str] = None,
        fullpath: Optional[os.PathLike] = None,
        prescision: int = 6,
    ):
        """Check the given list against a previously recorded version, or generate a new file.

        Parameters:
            data_list: The list to check.
            basename: The basename of the file to test/record. If not given the name of the test is used.
            fullpath: complete path to use as a reference file. This option will ignore ``datadir`` fixture when reading *expected* files but will still use it to write *obtained* files. Useful if a reference file is located in the session data dir for example.
            precision: The number of decimal places to round to when comparing floats.
        """
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
                object=data_list,
                path=serialized_name,
                datadir=self.datadir,
                original_datadir=self.original_datadir,
                request=self.request,
                with_test_class_names=self.with_test_class_names,
            )
            return

        # delete the previously created file if wasn't successful
        serialized_name.unlink(missing_ok=True)

        # if it needs to be checked, we need to round the float values to the same precision as the
        # reference file
        data = round_data(data_list.getInfo(), prescision)
        try:
            super().check(data, fullpath=data_name)

            # IF we are here it means the data has been modified so we edit the API call accordingly
            # to make sure next run will not be forced to call the API for a response.
            with suppress(BaseException):
                check_serialized(
                    object=data_list,
                    path=data_name,
                    datadir=self.datadir,
                    original_datadir=self.original_datadir,
                    request=self.request,
                    with_test_class_names=self.with_test_class_names,
                    force_regen=True,
                )

        except BaseException as e:
            raise e
