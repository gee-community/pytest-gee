Usage
=====

Installation
------------

Use pip to install **pytest-gee** in your environment:

.. code-block:: console

    pip install pytest-gee

It will then be automatically detected by ``pytest`` when you run your test suit.

Connect To Google Earth Engine
------------------------------

The main purpose of this plugin is to facilitate the connection to Google Earth Engine API in both CI/CD tests and local tests.
To do so, the lib will provide a number of connection methods that will hopefully cover your favorite way of connecting to GEE.

.. note::

    If you would like us to code an extra connection method please `open an issue <https://github.com/gee-community/pytest-gee/issues/new/choose>`__ on the github repo and never forget that contribution are very welcome!

.. note::

    All the methods presented in this section will fallback to a regular ``ee.Initialize()`` if the environment parameter are not found.
    This means that you can use this plugin in your local environment without having to change anything as long as the ``ee`` module is installed and that you already run once ``ee.Authenticate()``.

.. danger::

    Never forget that this method can potentially expose your personal credential to GEE so take some saety precaution before starting:

    - make sure the CI/CD platform support private variable (that are not exposed in the build logs)
    - make sure to review PR from new users before starting the build to make sure nobody steal your credentials
    - make sure the account you are using will have access to all the assets you need to run your tests
    - create small tests that will run quickly to make sure you don't overload your own GEE account with concurrent tasks

Private Token
^^^^^^^^^^^^^

The first method is to use a private token. This is the easiest way to connect to GEE in a CI/CD environment.

First authenticate to GEE API in your local computer using ``ee.Authenticate()``.

Then copy the ``credentials`` file content. This file is located in a different folder depending on the platform you use:

- Windows: ``C:\Users\USERNAME\\.config\\earthengine\\credentials``
- Linux: ``/home/USERNAME/.config/earthengine/credentials``
- MacOS: ``/Users/USERNAME/.config/earthengine/credentials``

Paste this content in your CI/CD environment in a ``EARTHENGINE_TOKEN`` variable.

Here is a github action example:

.. thumbnail:: _static/github_env_var.png
    :title: Github action environment variable setup

#. First go to the :guilabel:`settings`` of your Github repository
#. Then to :guilabel:`secretes and variables` -> :guilabel:`Actions`
#. In this page, set a :guilabel:`new repository secret` with the name ``EARTHENGINE_TOKEN`` and paste the content of your ``credentials`` file in the value field.

Since earthengine-api v0.1.370, it's not possible to use EE without providing a GCS project bucket. Save this value in a `EARTHENGINE_PROJECT` variable, it will be used in the method.

To make the variable available in your CI environment, you will need to add the following line in your action `.yaml` file:

.. code-block:: yaml

    # .github/action.yaml

    env:
        EARTHENGINE_TOKEN: ${{ secrets.EARTHENGINE_TOKEN }}
        EARTHENGINE_PROJECT: ${{ secrets.EARTHENGINE_PROJECT }}

    # The rest of your tests configuration

When working in your local environment export a ``EARTHENGINE_PROJECT`` variable as well:

.. code-block:: console

    export EARTHENGINE_PROJECT=ee-community

Finally you need to configure the ``pytest`` execution environment itself. Add the following line in your ``conftest.py`` file:

.. code-block:: python

    # conftest.py

    import pytest_gee


    def pytest_configure():
        pytest_gee.init_ee_from_token()

You are now ready to make API calls within your tests!

Service account
^^^^^^^^^^^^^^^

.. warning::

    This documentation assumes that you already have a Google cloud service account and that you have generated an API key for it. If not, please refer to Google own `documentation <https://cloud.google.com/iam/docs/keys-create-delete>` to proceed.

Paste this content of the `private-key.json` in your CI/CD environment in a ``EARTHENGINE_SERVICE_ACCOUNT`` variable.

Here is a github action example:

.. thumbnail:: _static/github_env_var.png
    :title: Github action environment variable setup

#. First go to the :guilabel:`settings`` of your Github repository
#. Then to :guilabel:`secretes and variables` -> :guilabel:`Actions`
#. In this page, set a :guilabel:`new repository secret` with the name ``EARTHENGINE_SERVICE_ACCOUNT`` and paste the content of your ``credentials`` file in the value field.

Currently when the earthengine-api is Initialized using a service account, the name of the associated cloud project is not detectable. It will prevent the initialization of the test folder generated from `pytest-gee`. To avoid this issue the method rely also on a ``EARTHENGINE_PROJECT`` env variable where you can set the name of your project.

To make the variable available in your CI environment, you will need to add the following line in your action `.yaml` file:

.. code-block:: yaml

    # .github/action.yaml

    env:
        EARTHENGINE_SERVICE_ACCOUNT: ${{ secrets.EARTHENGINE_SERVICE_ACCOUNT }}
        EARTHENGINE_PROJECT: ${{ secrets.EARTHENGINE_PROJECT }}

    # The rest of your tests configuration

When working in your local environment export a ``EARTHENGINE_PROJECT`` variable as well:

.. code-block:: console

    export EARTHENGINE_PROJECT=ee-community

Finally you need to configure the ``pytest`` execution environment itself. Add the following line in your ``conftest.py`` file:

.. code-block:: python

    # conftest.py

    import pytest_gee


    def pytest_configure():
        pytest_gee.init_ee_from_service_account()

You are now ready to make API calls within your tests!

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

Customize the test folder tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default the test folder tree is empty and will be deleted at the end of the test session.
You can decide to populate it with some assets that will be used in your tests.

To do so customize the ``gee_folder_structure`` fixture in your ``conftest.py`` file.
This fixture is a ``dict`` that will be used to create the folder tree in GEE.
First you can create containers assets (namely folders or image collections) to store your assets. These container are simply marked as keys in the dict and specify their types after a "::" symbol as shown in the following example.
assets need to be ``ee.Image`` or ``ee.FeatureCollection`` objects and remain small as the creation operation is taken care of by the plugin.
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
        return "users/username/my_root_folder"

.. note::

    This is compulsory if you use a service account to connect to GEE as the service account has no associated root folder.

Create assets
-------------

Most of tests pipelines are checking different python versions in parallel which can create multiple issues from a GEE perspective:

- The assets names need to be unique
- The tasks names need also to be unique

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
