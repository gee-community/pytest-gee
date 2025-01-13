"""implementation of the ``image_regression`` fixture."""

import os
from contextlib import suppress
from typing import Optional

import ee
import requests
from pytest_regressions.image_regression import ImageRegressionFixture

from .utils import build_fullpath, check_serialized


class ImageFixture(ImageRegressionFixture):
    """Fixture for regression testing of :py:class:`ee.Image`."""

    def check(
        self,
        data_image: ee.Image,
        diff_threshold: float = 0.1,
        expect_equal: bool = True,
        basename: Optional[str] = None,
        fullpath: Optional[os.PathLike] = None,
        scale: Optional[int] = 30,
        viz_params: Optional[dict] = None,
    ):
        """Check the given image against a previously recorded version, or generate a new file.

        This method will create a thumnail version of the requested image. It is made to allow a human user to check the result of the
        Computation. The thumbnail will be computed on the fly using earthengine. This mean that the test must be reasonable in size and scale.
        We will perform no feasibility checks and your computation might crash if you are too greedy.
        The input image will be either a single band image (displayed using black&white colormap) or a 3 band image (displayed using as fake RGB bands).
        If the ``viz_params`` parameter is omitted then it will detect the available ands, and use default viz params.

        Parameters:
            data_image: The image to check. The image needs to be clipped to a geometry or have an existing footprint.
            diff_threshold: The threshold for the difference between the expected and obtained images.
            expect_equal: If ``True`` the images are expected to be equal, otherwise they are expected to be different.
            basename: The basename of the file to test/record. If not given the name of the test is used.
            fullpath: complete path to use as a reference file. This option will ignore ``datadir`` fixture when reading *expected* files but will still use it to write *obtained* files. Useful if a reference file is located in the session data dir for example.
            scale: The scale to use for the thumbnail.
            viz_params: The visualization parameters to use for the thumbnail. If not given, the min and max values of the image will be used.
        """
        # rescale the original image
        geometry = data_image.geometry()
        data_image = data_image.clipToBoundsAndScale(geometry, scale=scale)

        # build the different filename to be consistent between our 3 checks
        data_name = build_fullpath(
            datadir=self.original_datadir,
            request=self.request,
            extension=".png",
            basename=basename,
            fullpath=fullpath,
            with_test_class_names=self.with_test_class_names,
        )
        serialized_name = data_name.with_stem(f"serialized_{data_name.stem}").with_suffix(".yml")

        # check the previously registered serialized call from GEE. If it matches the current call,
        # we don't need to check the data
        with suppress(BaseException):
            check_serialized(
                object=data_image,
                path=serialized_name,
                datadir=self.datadir,
                original_datadir=self.original_datadir,
                request=self.request,
                with_test_class_names=self.with_test_class_names,
            )
            return

        # delete the previously created file if wasn't successful
        serialized_name.unlink(missing_ok=True)

        # extract min and max for visualization
        minMax = data_image.reduceRegion(ee.Reducer.minMax(), geometry, scale)

        # create visualization parameters based on the computed minMax values
        if viz_params is None:
            nbBands = ee.Algorithms.If(data_image.bandNames().size().gte(3), 3, 1)
            bands = data_image.bandNames().slice(0, ee.Number(nbBands))
            min = bands.map(lambda b: minMax.get(ee.String(b).cat("_min")))
            max = bands.map(lambda b: minMax.get(ee.String(b).cat("_max")))
            viz_params = ee.Dictionary({"bands": bands, "min": min, "max": max}).getInfo()

        # get the thumbnail image
        thumb_url = data_image.getThumbURL(params=viz_params)
        byte_data = requests.get(thumb_url).content

        # if it needs to be checked, we need to round the float values to the same precision as the
        # reference file
        try:
            super().check(byte_data, diff_threshold, expect_equal, fullpath=data_name)

            # IF we are here it means the data has been modified so we edit the API call accordingly
            # to make sure next run will not be forced to call the API for a response.
            with suppress(BaseException):
                check_serialized(
                    object=data_image,
                    path=data_name,
                    datadir=self.datadir,
                    original_datadir=self.original_datadir,
                    request=self.request,
                    with_test_class_names=self.with_test_class_names,
                    force_regen=True,
                )

        except BaseException as e:
            raise e
