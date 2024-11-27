"""Implementation of the ``dictionary_regression`` fixture."""
import os
from typing import Optional

import ee
from pytest_regressions.data_regression import DataRegressionFixture

from .utils import round_data


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
        # round any float value before serving the data to the check function
        data_dict = round_data(data_dict.getInfo(), prescision)
        super().check(data_dict, basename=basename, fullpath=fullpath)
