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

Private Token
^^^^^^^^^^^^^

The first method is to use a private token. This is the easiest way to connect to GEE in a CI/CD environment.

.. danger::

    Never forget that this method can potentially expose your personal credential to GEE so take some saety precaution before starting:

    - make sure the CI/CD platform support private variable (that are not exposed in the build logs)
    - make sure to review PR from new users before starting the build to make sure nobody steal your credentials
    - make sure the account you are using will have access to all the assets you need to run your tests
    - create small tests that will run quickly to make sure you don't overload your own GEE account with concurrent tasks

First authenticate to GEE API in your local computer using ``ee.Authenticate()``.

Then copy the ``credentials`` file content. This file is located in a different folder depending on the platform you use:

- Windows: ``C:\Users\USERNAME\\.config\\earthengine\\credentials``
- Linux: ``/home/USERNAME/.config/earthengine/credentials``
- MacOS: ``/Users/USERNAME/.config/earthengine/credentials``

Paste this content in your CI/CD environment in a ``EARTHENGINE_TOKEN`` variable.

Here is a github action example:

.. thumbnail:: _static/github_env_var.png
    :title: Github action environment variable setup

1. First go to the :guilabel:`settings`` of your Github repository
1. Then to :guilabel:`secretes and variables` -> :guilabel:`Actions`
1. In this page, set a :guilabel:`new repository secret` with the name ``EARTHENGINE_TOKEN`` and paste the content of your ``credentials`` file in the value field.

To make the variable available in your CI environment, you will need to add the following line in your action `.yaml` file:

.. code-block:: yaml

    # .github/action.yaml

    env:
        EARTHENGINE_TOKEN: ${{ secrets.EARTHENGINE_TOKEN }}

    # The rest of your tests configuration

Finally you need to configure the ``pytest`` execution environment itself. Add the following line in your ``conftest.py`` file:

.. code-block:: python

    # conftest.py

    import pytest_gee


    def pytest_configure():
        pytest_gee.init_ee_from_token()

You are now ready to make API calls within your tests!

Create assets
-------------

Most of tests pipelines are checking different python versions in parallel which can create multiple issues from a GEE perspective:

- The assets names need to be unique
- the tasks names need also to be unique

To avoid this issue, the plugin is shipped with a session wise unique hex fixture that can be used to suffix or prefix your assets and tasks names.

.. code-block:: python

    # test.py

    import pytest


    def test_create_asset(gee_hash):
        asset_name = f"asset_{gee_hash}"
        # Do something with the asset name
