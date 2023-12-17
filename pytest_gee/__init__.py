"""The init file of the package."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Union

import ee
import httplib2

from pytest_gee import utils

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
    return utils.wait(task, timeout)


def delete_assets(asset_id: Union[str, Path], dry_run: bool = True) -> list:
    """Delete the selected asset and all its content.

    This method will delete all the files and folders existing in an asset folder.
    By default a dry run will be launched and if you are satisfyed with the displayed names, change the ``dry_run`` variable to ``False``.
    No other warnng will be displayed.

    .. warning::

        If this method is used on the root directory you will loose all your data, it's highly recommended to use a dry run first and carefully review the destroyed files.

    Args:
        asset_id: the Id of the asset or a folder
        dry_run: whether or not a dry run should be launched. dry run will only display the files name without deleting them.

    Returns:
        a list of all the files deleted or to be deleted
    """
    asset_id = str(asset_id)
    # define a delete function to change the behaviour of the method depending of the mode
    # in dry mode, the function only store the assets to be destroyed as a dictionary.
    # in non dry mode, the function store the asset names in a dictionary AND delete them.
    output = []

    def delete(id: str):
        output.append(id)
        dry_run is True or ee.data.deleteAsset(id)

    # identify the type of asset
    asset_info = ee.data.getAsset(asset_id)

    if asset_info["type"] == "FOLDER":

        # get all the assets
        asset_list = utils.get_assets(folder=asset_id)

        # split the files by nesting levels
        # we will need to delete the more nested files first
        assets_ordered: dict = {}
        for asset in asset_list:
            lvl = len(asset["id"].split("/"))
            assets_ordered.setdefault(lvl, [])
            assets_ordered[lvl].append(asset)

        # delete all items starting from the more nested one but not folders
        assets_ordered = dict(sorted(assets_ordered.items(), reverse=True))
        for lvl in assets_ordered:
            for i in assets_ordered[lvl]:
                delete(i["name"])

    # delete the initial folder/asset
    delete(asset_id)

    return output


def init_tree(structure: dict, prefix: str, account_root: str) -> Path:
    """Create an EarthEngine folder tree from a dictionary.

    The input ditionary should described the structure of the folder you want to create.
    The keys are the folder names and the values are the subfolders.
    Once you reach an ``ee.FeatureCollection`` and/or an ``ee.Image`` set it in the dictionary and the function will export the object.

    Args:
        structure: the structure of the folder to create
        prefix: the prefix to use on every item (folder, tasks, asset_id, etc.)
        account_root: the root folder of the test where to create the test folder.

    Returns:
        the path of the created folder

    Examples:
        >>> structure = {
        ...     "folder_1": {
        ...         "image": ee.image(1),
        ...         "fc": ee.FeatureCollection(ee.Geometry.Point([0, 0])),
        ...     },
        ... }
        ... init_tree(structure, "toto")
    """
    # recursive function to create the folder tree
    def _recursive_create(structure, prefix, folder):
        for name, content in structure.items():
            if isinstance(content, dict):
                loc_folder = f"{folder}/{prefix}_{name}"
                ee.data.createAsset({"type": "FOLDER"}, loc_folder)
                _recursive_create(content, prefix, loc_folder)
            else:
                utils.export_asset(content, Path(folder) / f"{prefix}_{name}")

    # create the root folder
    account_root = ee.data.getAssetRoots()[0]["id"]
    root_folder = f"{account_root}/{prefix}"
    ee.data.createAsset({"type": "FOLDER"}, root_folder)

    # start the recursive function
    _recursive_create(structure, prefix, root_folder)

    return Path(root_folder)
