GEE Filesystem
==============

Generate a test file tree in GEE
--------------------------------

Using the ``pytest_gee`` plugin, you can easily generate a test file tree in GEE that will be used to run your tests.
This tree will start in a folder named with the ``gee_hash`` fixture and will be deleted at the end of the test session.

By using this method you will ensure that the folder you are using for your test is unique and that it will not interfere with other tests (e.g. parallel tests).

.. code-block:: python

    # test_something.py

    def test_something(gee_hash, gee_folder_root, gee_test_folder):
        # this folder is existing within your GEE account and will be deleted at the end of the test session
        print(gee_folder_root)

.. warning::

    To avoid piling up fake folder in your GEE account, make sure to let the test reach the end of the session.
    It means that you should **never** cancel a session with ``ctrl+c`` or by killing the process.


Customize the test folder tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default the test folder tree is empty and will be deleted at the end of the test session.
You can decide to populate it with some assets that will be used in your tests.

To do so customize the ``gee_folder_structure`` fixture in your ``conftest.py`` file.
This fixture is a ``dict`` that will be used to create the folder tree in GEE.
First you can create containers assets (namely folders or image collections) to store your assets.
These container are simply marked as keys in the dict and specify their types after a "::" symbol as shown in the following example.
assets need to be ``ee.Image`` or ``ee.FeatureCollection`` objects and remaining small as the creation operation is taken care of by the plugin.
Specifically for ``ee.Image`` objects, please use the ``clipToBoundsAndScale`` method to make sure the asset has a geometry and a scale.

.. code-block:: python

    # conftest.py

    import pytest

    @pytest.fixture(scope="session")
    def gee_folder_structure():
        """Override the default test folder structure."""
        point = ee.Geometry.Point([0, 0])
        return {
            "folder::Folder": {
                "image": ee.Image(1).clipToBoundsAndScale(point.buffer(100), scale=30),
                "fc": ee.FeatureCollection(point),
            },
            "image_collection::ImageCollection": {
                "image1": ee.Image(1).clipToBoundsAndScale(point.buffer(100), scale=30),
                "image2": ee.Image(1).clipToBoundsAndScale(point.buffer(100), scale=30),
            }
        }

Which will render in your GEE account as:

.. code-block::

    8d98a5be574041a6a54d6def9d915c67/
    └── folder/
        ├── fc (FeatureCollection)
        └── image (Image)
    └── image_collection/ (ImageCollection)
        ├── image1 (Image)
        └── image2 (Image)

Customize the root folder
^^^^^^^^^^^^^^^^^^^^^^^^^

By default the test folder will be created at the root of the user account. There are situation where one could prefer to store it in a specific folder.

To do so customize the ``gee_folder_root`` fixture in your ``conftest.py`` file, simply return the asset id of the folder you want to use as root.

.. code-block:: python

    # conftest.py

    import pytest

    @pytest.fixture(scope="session")
    def gee_folder_root():
        """Override the default test folder root."""
        return "project/username/assets/my_root_folder"

.. note::

    This is compulsory if you use a service account to connect to GEE as the service account has no associated root folder.

Create assets
-------------

Most of tests pipelines are checking different python versions in parallel which can create multiple issues from a GEE perspective:

- The assets names need to be unique
- The tasks names also need to be unique

To avoid this issue, the plugin is shipped with a session wise unique hex fixture ``gee_hash`` that can be used to suffix or prefix your assets and tasks names.
To make sure the asset exist when you run your tests, you can use the ``pytest_gee.wait`` method to wait until the asset is effectively generated.

.. code-block:: python

    # test.py

    import pytest
    import pytest_gee


    def test_create_asset(gee_hash):
        # create an asset name
        asset_name = f"asset_{gee_hash}"

        # export the an object to this asset
        task = ee.batch.Export.image.toAsset(
            image=ee.Image(1),
            description=asset_name,
            assetId=asset_name,
            scale=1,
            maxPixels=1e9,
        )
        task.start()

        # wait for the asset to be created
        pytest_gee.wait(task)

        # Do something with the asset name
