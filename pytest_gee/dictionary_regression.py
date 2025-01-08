"""Implementation of the ``dictionary_regression`` fixture."""
import os
from contextlib import suppress
from typing import Optional

import ee
from pytest_regressions.data_regression import DataRegressionFixture

from .utils import build_fullpath, round_data


class DictionaryFixture(DataRegressionFixture):
    """Fixture for regression testing of :py:class:`ee.Dictionary`."""

    def check(
        self,
        data_dict: ee.Dictionary,
        basename: Optional[str] = None,
        fullpath: Optional[os.PathLike] = None,
        prescision: int = 6,
    ):
        """Check the given list against a previously recorded version, or generate a new file.

        Parameters:
            data_dict: The dictionary to check.
            basename: The basename of the file to test/record. If not given the name of the test is used.
            fullpath: complete path to use as a reference file. This option will ignore ``datadir`` fixture when reading *expected* files but will still use it to write *obtained* files. Useful if a reference file is located in the session data dir for example.
            precision: The number of decimal places to round to when comparing floats.
        """
        # build the different filename to be consistent between our 3 checks
        name = build_fullpath(
            self.original_datadir, self.request, "", basename, fullpath, self.with_test_class_names
        )
        serialized_name = name.with_stem(f"serialized_{name.name}").with_suffix(".yml")
        data_name = name.with_suffix(".yml")

        # check the previously registered serialized call from GEE. If it matches the current call,
        # we don't need to check the data
        serialized = data_dict.serialize()
        with suppress(BaseException):
            super().check(serialized, fullpath=serialized_name)
            return

        # if it needs to be checked, we need to round the float values to the same precision as the
        # reference file
        data_list = round_data(data_dict.getInfo(), prescision)
        try:
            super().check(data_list, fullpath=data_name)

            # IF we are here it means the data has been modified so we edit the API call accordingly
            # to make sure next run will not be forced to call the API for a response.
            serialized_name.unlink(missing_ok=True)
            with suppress(BaseException):
                super().check(serialized, fullpath=serialized_name)

        except BaseException as e:
            raise e
