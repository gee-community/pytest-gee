"""functions used to build the API that we don't want to expose to end users.

.. danger::

    This module is for internal use only and should not be used directly.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import List, Optional, Union
from warnings import warn

import ee
from deprecated.sphinx import deprecated
from ee.cli.utils import wait_for_task


@deprecated(version="0.3.5", reason="Use the vanilla GEE ``wait_for_task`` function instead.")
def wait(task: Union[ee.batch.Task, str], timeout: int = 10 * 60) -> str:
    """Wait until the selected process is finished or we reached timeout value.

    Args:
        task: name of the running task or the Task object itself.
        timeout: timeout in seconds. if set to 0 the parameter is ignored. default to 1 minutes.

    Returns:
        the final state of the task
    """
    task_id = task.id if isinstance(task, ee.batch.Task) else task
    return wait_for_task(task_id, timeout, log_progress=False)


def get_task(task_descripsion: str) -> Optional[ee.batch.Task]:
    """Search for the described task in the user Task list return None if nothing is found.

    Args:
        task_descripsion: the task description

    Returns:
        return the found task else None
    """
    task = None
    for t in ee.batch.Task.list():
        if t.config["description"] == task_descripsion:
            task = t
            break

    return task


def get_assets(folder: Union[str, Path]) -> List[dict]:
    """Get all the assets from the parameter folder. every nested asset will be displayed.

    Args:
        folder: the initial GEE folder

    Returns:
        the asset list. each asset is a dict with 3 keys: 'type', 'name' and 'id'
    """
    # set the folder and init the list
    asset_list: list = []
    folder = folder if isinstance(folder, str) else folder.as_posix()

    # recursive function to get all the assets
    def _recursive_get(folder, asset_list):
        for asset in ee.data.listAssets({"parent": folder})["assets"]:
            asset_list.append(asset)
            if asset["type"] in ["FOLDER", "IMAGE_COLLECTION"]:
                asset_list = _recursive_get(asset["name"], asset_list)
        return asset_list

    return _recursive_get(folder, asset_list)


def export_asset(
    object: ee.ComputedObject, asset_id: Union[str, Path], description: str
) -> PurePosixPath:
    """Export assets to the GEE platform, only working for very simple objects.

    ARgs:
        object: the object to export
        asset_id: the name of the asset to create
        description: the description of the task

    Returns:
        the path of the created asset
    """
    # convert the asset_id to a string note that GEE only supports unix style separator
    asset_id = asset_id if isinstance(asset_id, str) else asset_id.as_posix()

    if isinstance(object, ee.FeatureCollection):
        task = ee.batch.Export.table.toAsset(
            collection=object,
            description=description,
            assetId=asset_id,
        )
    elif isinstance(object, ee.Image):
        task = ee.batch.Export.image.toAsset(
            region=object.geometry(),
            image=object,
            description=description,
            assetId=asset_id,
        )
    else:
        raise ValueError("Only ee.Image and ee.FeatureCollection are supported")

    # launch the task and wait for the end of exportation
    task.start()
    wait_for_task(task.id, 10 * 60, False)

    return PurePosixPath(asset_id)


def _create_container(asset_request: str) -> str:
    """Create a container for the asset request depending on the requested type.

    Args:
        asset_request: the asset request specifying the type of asset to create. Convention is <asset_id>::<asset_type>

    Returns:
        the asset_id of the container
    """
    # deprecation management for older version of the lib
    parts = asset_request.split("::")
    if len(parts) == 1:
        parts.append("Folder")
        warn(f"Asset {asset_request} is not specifying asset Type, it will be created as a FOLDER.")

    # extract the asset_id and the asset_type from the different parts
    # if more than 2 splits are identified they will be ignored
    asset_id, asset_type = parts[:2]

    # create the container
    if asset_type in ["Folder", "ImageCollection"]:
        ee.data.createAsset({"type": asset_type}, asset_id)
    else:
        raise ValueError(f"Asset type {asset_type} is not supported.")

    return asset_id


def init_tree(structure: dict, prefix: str, root: Union[str, PurePosixPath]) -> PurePosixPath:
    """Create an EarthEngine folder tree from a dictionary.

    The input ditionary should described the structure of the folder you want to create.
    The keys are the folder names and the values are the subfolders.
    Once you reach an ``ee.FeatureCollection`` and/or an ``ee.Image`` set it in the dictionary and the function will export the object.

    Args:
        structure: the structure of the folder to create
        prefix: the prefix to use on every item (folder, tasks, asset_id, etc.)
        root: the root folder of the test where to create the test folder.

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
            asset_id = PurePosixPath(folder) / name
            description = f"{prefix}_{name}"
            if isinstance(content, dict):
                asset_id = _create_container(str(asset_id))
                _recursive_create(content, prefix, asset_id)
            else:
                export_asset(content, asset_id, description)

    # create the root folder
    root = PurePosixPath(root) if isinstance(root, str) else root
    root_folder = f"{root.as_posix()}/{prefix}"
    ee.data.createFolder(root_folder)

    # start the recursive function
    _recursive_create(structure, prefix, root_folder)

    return PurePosixPath(root_folder)


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
    # convert the asset_id to a string
    asset_id = asset_id if isinstance(asset_id, str) else asset_id.as_posix()

    # define a delete function to change the behaviour of the method depending of the mode
    # in dry mode, the function only store the assets to be destroyed as a dictionary.
    # in non dry mode, the function store the asset names in a dictionary AND delete them.
    output = []

    def delete(id: str):
        output.append(id)
        dry_run is True or ee.data.deleteAsset(id)

    # identify the type of asset
    asset_info = ee.data.getAsset(asset_id)

    if asset_info["type"] in ["FOLDER", "IMAGE_COLLECTION"]:

        # get all the assets
        asset_list = get_assets(folder=asset_id)

        # split the files by nesting levels
        # we will need to delete the more nested files first
        assets_ordered: dict = {}
        for asset in asset_list:
            lvl = len(asset["id"].split("/"))
            assets_ordered.setdefault(lvl, [])
            assets_ordered[lvl].append(asset)

        # delete all items starting from the more nested ones
        assets_ordered = dict(sorted(assets_ordered.items(), reverse=True))
        print(assets_ordered)
        for lvl in assets_ordered:
            for i in assets_ordered[lvl]:
                delete(i["name"])

    # delete the initial folder/asset
    delete(asset_id)

    return output
