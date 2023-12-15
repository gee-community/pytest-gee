"""functions used to build the API that we don't want to expose to end users.

.. danger::

    This module is for internal use only and should not be used directly.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union

import ee


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
    asset_list = []
    folder = str(folder)

    # recursive function to get all the assets
    def _recursive_get(folder, asset_list):
        for asset in ee.data.listAssets({"parent": folder})["assets"]:
            asset_list.append(asset)
            if asset["type"] == "FOLDER":
                asset_list = _recursive_get(asset["name"], asset_list)
        return asset_list

    return _recursive_get(folder, asset_list)
