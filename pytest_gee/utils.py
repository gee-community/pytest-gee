"""functions used to build the API that we don't want to expose to end users.

.. danger::

    This module is for internal use only and should not be used directly.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional, Union

import ee


def wait(task: Union[ee.batch.Task, str], timeout: int = 60) -> str:
    """Wait until the selected process is finished or we reached timeout value.

    Args:
        task: name of the running task or the Task object itself.
        timeout: timeout in seconds. if set to 0 the parameter is ignored. default to 1 minutes.

    Returns:
        the final state of the task
    """
    # give 5 seconds of delay to GEE to make sure the task is created
    time.sleep(5)

    # init both the task object and the state
    task = task if isinstance(task, ee.batch.Task) else get_task(task)
    assert task is not None, "The task is not found"
    state = "UNSUBMITTED"

    # loop every 5s to check the task state. This is blocking the Python interpreter
    start_time = time.time()
    while state != "COMPLETED" and time.time() - start_time < timeout:
        time.sleep(5)
        state = task.state
        if state == "FAILED":
            break

    return state


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
    folder = str(folder)

    # recursive function to get all the assets
    def _recursive_get(folder, asset_list):
        for asset in ee.data.listAssets({"parent": folder})["assets"]:
            asset_list.append(asset)
            if asset["type"] == "FOLDER":
                asset_list = _recursive_get(asset["name"], asset_list)
        return asset_list

    return _recursive_get(folder, asset_list)


def export_asset(object: ee.ComputedObject, asset_id: Union[str, Path]) -> Path:
    """Export assets to the GEE platform, only working for very simple objects.

    ARgs:
        object: the object to export
        asset_id: the name of the asset to create

    Returns:
        the path of the created asset
    """
    asset_id = Path(asset_id)
    if isinstance(object, ee.FeatureCollection):
        task = ee.batch.Export.table.toAsset(
            collection=object,
            description=asset_id.stem,
            assetId=str(asset_id),
        )
    elif isinstance(object, ee.Image):
        task = ee.batch.Export.image.toAsset(
            region=object.geometry(),
            image=object,
            description=asset_id.stem,
            assetId=str(asset_id),
        )
    else:
        raise ValueError("Only ee.Image and ee.FeatureCollection are supported")

    # launch the task and wait for the end of exportation
    task.start()
    wait(asset_id.stem)

    return asset_id
