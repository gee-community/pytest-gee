"""implementation of the ``image_regression`` fixture."""
from typing import Optional

import ee
import requests
from pytest_regressions.image_regression import ImageRegressionFixture


class ImageFixture(ImageRegressionFixture):
    """Fixture for regression testing of :py:class:`ee.Image`."""

    def check(
        self,
        data_image: ee.Image,
        diff_threshold: float = 0.1,
        expect_equal: bool = True,
        basename: Optional[str] = None,
        scale: Optional[int] = 30,
    ):
        """Check the given image against a previously recorded version, or generate a new file.

        This method will create a thumnail version of the requested image. It is made to allow a human user to check the result of the
        Computation. The thumbnail will be computed on the fly using earthengine. This mean that the test must be reasonable in size and scale.
        We will perform no feasibility checks and your computation might crash if you are too greedy.
        The input image will be either a single band image (displayed using black&white colormap) or a 3 band image (displayed using as fake RGB bands).

        Parameters:
            data_image: The image to check. The image needs to be clipped to a geometry or have an existing footprint.
            diff_threshold: The threshold for the difference between the expected and obtained images.
            expect_equal: If ``True`` the images are expected to be equal, otherwise they are expected to be different.
            basename: The basename of the file to test/record. If not given the name of the test is used.
            scale: The scale to use for the thumbnail.
        """
        # grescale the original image
        geometry = data_image.geometry()
        image = data_image.clipToBoundsAndScale(geometry, scale=scale)

        # extract min and max for visualization
        minMax = image.reduceRegion(ee.Reducer.minMax(), geometry, scale)

        # create visualization parameters based on the computed minMax values
        bands = image.bandNames()
        min = bands.map(lambda b: minMax.get(ee.String(b).cat("_min")))
        max = bands.map(lambda b: minMax.get(ee.String(b).cat("_max")))
        viz = ee.Dictionary({"bands": bands, "min": min, "max": max}).getInfo()

        # get the thumbnail image
        thumb_url = image.getThumbURL(params=viz)
        byte_data = requests.get(thumb_url).content

        # call the parent check method
        super().check(byte_data, diff_threshold, expect_equal, basename=basename)
