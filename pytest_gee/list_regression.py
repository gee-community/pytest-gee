"""Implementation of the ``list_regression`` fixture."""

import os
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

        is_serialized_equal = check_serialized(
            object=data_list,
            path=serialized_name,
            datadir=self.datadir,
            request=self.request,
        )

        if is_serialized_equal:
            # serialized is equal? -> pass test
            # TODO: add proper logging
            return
        else:
            # if it needs to be checked, we need to round the float values to the same precision as the
            # reference file
            data = round_data(data_list.getInfo(), prescision)

            # check query result
            super().check(data, fullpath=data_name)

            # if we are here it means that the query result is equal but the serialized is not -> regenerate serialized
            serialized_name.unlink(missing_ok=True)
            check_serialized(
                object=data_list,
                path=serialized_name,
                datadir=self.datadir,
                request=self.request,
            )
