
pytest-gee
==========

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg?logo=opensourceinitiative&logoColor=white
    :target: LICENSE
    :alt: License: MIT

.. image:: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?logo=git&logoColor=white
   :target: https://conventionalcommits.org
   :alt: conventional commit

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black badge

.. image:: https://img.shields.io/badge/code_style-prettier-ff69b4.svg?logo=prettier&logoColor=white
   :target: https://github.com/prettier/prettier
   :alt: prettier badge

.. image:: https://img.shields.io/badge/pre--commit-active-yellow?logo=pre-commit&logoColor=white
    :target: https://pre-commit.com/
    :alt: pre-commit

.. image:: https://img.shields.io/pypi/v/pytest-gee?color=blue&logo=pypi&logoColor=white
    :target: https://pypi.org/project/pytest-gee/
    :alt: PyPI version

.. image:: https://img.shields.io/conda/vn/conda-forge/pytest-gee?logo=anaconda&logoColor=white&color=blue
    :target: https://anaconda.org/conda-forge/pytest-gee
    :alt: conda-forge version badge

.. image:: https://img.shields.io/github/actions/workflow/status/gee-community/pytest-gee/unit.yaml?logo=github&logoColor=white
    :target: https://github.com/gee-community/pytest-gee/actions/workflows/unit.yaml
    :alt: build

.. image:: https://img.shields.io/codecov/c/github/gee-community/pytest-gee?logo=codecov&logoColor=white
    :target: https://codecov.io/gh/gee-community/pytest-gee
    :alt: Test Coverage

.. image:: https://img.shields.io/readthedocs/pytest-gee?logo=readthedocs&logoColor=white
    :target: https://pytest-gee.readthedocs.io/en/latest/
    :alt: Documentation Status

Overview
--------

.. image:: https://raw.githubusercontent.com/gee-community/pytest-gee/main/docs/_static/logo.svg
    :width: 20%
    :align: right

``pytest-gee`` provides some fixtures that make it easy to generate independent tests that require Earth Engine asset filesystem.
It also able to help maintaining tests that generate Earth Engine server side data.

This plugin uses a data directory (courtesy of ``pytest-datadir``) to store expected data files,
which are stored and used as baseline for future test runs.
You can also define your own data directory directly as described in the ``pytest_regression`` documentation.

Credits
-------

This package was created with `Copier <https://copier.readthedocs.io/en/latest/>`__ and the `@12rambau/pypackage <https://github.com/12rambau/pypackage>`__ 0.1.11 project template.
