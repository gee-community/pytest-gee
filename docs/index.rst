:html_theme.sidebar_secondary.remove:


pytest-gee
==========

.. image:: _static/logo.png
    :width: 20%
    :align: right
    :class: dark-light


``pytest-gee`` provides some fixtures that make it easy to generate independent tests that require Earth Engine asset filesystem.
It also able to help maintaining tests that generate Earth Engine server side data.

This plugin uses a data directory (courtesy of ``pytest-datadir``) to store expected data files,
which are stored and used as baseline for future test runs.
You can also define your own data directory directly as described in the ``pytest_regression`` documentation.

.. toctree::
   :hidden:

   content/installation
   content/filesystem
   content/regression
   content/contribute
