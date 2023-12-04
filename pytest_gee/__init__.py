"""The init file of the package."""
import os
from pathlib import Path

import ee
import httplib2

__version__ = "0.2.0"
__author__ = "Pierrick Rambaud"
__email__ = "pierrick.rambaud49@gmail.com"


def init_ee_from_token():
    r"""Initialize earth engine according using a token.

    THe environment used to run the tests need to have a EARTHENGINE_TOKEN variable.
    The content of this variable must be the copy of a personal credential file that you can find on your local computer if you already run the earth engine command line tool. See the usage question for a github action example.

    - Windows: ``C:\Users\USERNAME\\.config\\earthengine\\credentials``
    - Linux: ``/home/USERNAME/.config/earthengine/credentials``
    - MacOS: ``/Users/USERNAME/.config/earthengine/credentials``

    Note:
        As all init method of pytest-gee, this method will fallback to a regular ``ee.Initialize()`` if the environment variable is not found e.g. on your local computer.
    """
    if "EARTHENGINE_TOKEN" in os.environ:

        # write the token to the appropriate folder
        ee_token = os.environ["EARTHENGINE_TOKEN"]
        credential_folder_path = Path.home() / ".config" / "earthengine"
        credential_folder_path.mkdir(parents=True, exist_ok=True)
        credential_file_path = credential_folder_path / "credentials"
        credential_file_path.write_text(ee_token)

    # if the user is in local development the authentication should
    # already be available
    ee.Initialize(http_transport=httplib2.Http())
