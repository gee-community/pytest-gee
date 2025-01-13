"""The init file of the package."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Union

import ee
import httplib2
from deprecated.sphinx import deprecated
from ee.cli.utils import wait_for_task

__version__ = "0.6.1"
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
        # read the ee_token from the environment variable
        ee_token = os.environ["EARTHENGINE_TOKEN"]

        # small workaround to remove the quotes around the token
        # related to a very specific issue with readthedocs interface
        # https://github.com/readthedocs/readthedocs.org/issues/10553
        pattern = re.compile(r"^'[^']*'$")
        ee_token = ee_token[1:-1] if pattern.match(ee_token) else ee_token

        # write the token to the appropriate folder
        credential_folder_path = Path.home() / ".config" / "earthengine"
        credential_folder_path.mkdir(parents=True, exist_ok=True)
        credential_file_path = credential_folder_path / "credentials"
        credential_file_path.write_text(ee_token)

    project_id = os.environ.get("EARTHENGINE_PROJECT", ee.data._cloud_api_user_project)
    if project_id is None:
        raise ValueError(
            "The project name cannot be detected."
            "Please set the EARTHENGINE_PROJECT environment variable."
        )

    # if the user is in local development the authentication should
    # already be available
    ee.Initialize(project=project_id, http_transport=httplib2.Http())


def init_ee_from_service_account():
    """Initialize earth engine according using a service account.

    The environment used to run the tests need to have a EARTHENGINE_SERVICE_ACCOUNT variable.
    The content of this variable must be the copy of a personal credential file that you can generate from the google cloud console.

    Note:
        As all init method of ``pytest-gee``, this method will fallback to a regular ``ee.Initialize`` using the ``EARTHENGINE_PROJECT`` environment variable.
    """
    if "EARTHENGINE_SERVICE_ACCOUNT" in os.environ:
        # extract the environment variables data
        private_key = os.environ["EARTHENGINE_SERVICE_ACCOUNT"]

        # small workaround to remove the quotes around the token
        # related to a very specific issue with readthedocs interface
        # https://github.com/readthedocs/readthedocs.org/issues/10553
        pattern = re.compile(r"^'[^']*'$")
        private_key = private_key[1:-1] if pattern.match(private_key) else private_key

        # connect to GEE using a temp file to avoid writing the key to disk
        with tempfile.TemporaryDirectory() as temp_dir:
            file = Path(temp_dir) / "private_key.json"
            file.write_text(private_key)
            ee_user = json.loads(private_key)["client_email"]
            credentials = ee.ServiceAccountCredentials(ee_user, str(file))
            ee.Initialize(credentials=credentials, http_transport=httplib2.Http())

    elif "EARTHENGINE_PROJECT" in os.environ:
        # if the user is in local development the authentication should already be available
        # we simply need to use the provided project name
        ee.Initialize(project=os.environ["EARTHENGINE_PROJECT"], http_transport=httplib2.Http())

    else:
        raise ValueError(
            "EARTHENGINE_SERVICE_ACCOUNT or EARTHENGINE_PROJECT environment variable is missing"
        )


@deprecated(version="0.3.5", reason="Use the vanilla GEE ``wait_for_task`` function instead.")
def wait(task: Union[ee.batch.Task, str], timeout: int = 5 * 60) -> str:
    """Wait until the selected process is finished or we reached timeout value.

    Args:
        task: name of the running task or the Task object itself.
        timeout: timeout in seconds. if set to 0 the parameter is ignored. default to 5 minutes.

    Returns:
        the final state of the task
    """
    # just expose the utils function
    # this is compulsory as wait is also needed in the utils module
    task_id = task.id if isinstance(task, ee.batch.Task) else task
    return wait_for_task(task_id, timeout, log_progress=False)
