:html_theme.sidebar_secondary.remove:


pytest-gee
==========

``pytest-gee`` provides some fixtures that make it easy to generate independent tests that require Earth Engine asset filesystem.
It also able to help maintaining tests that generate Earth Engine server side data.

This plugin uses a data directory (courtesy of ``pytest-datadir``) to store expected data files,
which are stored and used as baseline for future test runs.
You can also define your own data directory directly as described in the ``pytest_regression`` documentation.

.. toctree::
   :hidden:

   content/usage
   content/contribute

Documentation contents
----------------------

The documentation contains 3 main sections:

.. grid:: 1 2 3 3

   .. grid-item::

      .. card:: Usage
         :link: usage.html

         Usage and installation

   .. grid-item::

      .. card:: Contribute
         :link: contribute.html

         Help us improve the lib.

   .. grid-item::

      .. card:: API
         :link: autoapi/index.html

         Discover the lib API.
