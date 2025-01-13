"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Path setup ----------------------------------------------------------------
from datetime import datetime

# -- Project information -------------------------------------------------------
project = "pytest-gee"
author = "Pierrick Rambaud"
copyright = f"2020-{datetime.now().year}, {author}"
release = "0.6.1"

# -- General configuration -----------------------------------------------------
extensions = [
    "sphinx_copybutton",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "autoapi.extension",
]
exclude_patterns = ["**.ipynb_checkpoints"]
templates_path = ["_template"]

# -- Options for HTML output ---------------------------------------------------
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_logo = "_static/long-logo.png"
html_favicon = "_static/logo.png"
html_sidebars = {"content/*": []}
html_theme_options = {
    "use_edit_page_button": True,
    "footer_end": ["theme-version", "pypackage-credit"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/gee-community/pytest-gee",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "Pypi",
            "url": "https://pypi.org/project/pytest-gee/",
            "icon": "fa-brands fa-python",
        },
        {
            "name": "Conda",
            "url": "https://anaconda.org/conda-forge/pytest-gee",
            "icon": "fa-custom fa-conda",
            "type": "fontawesome",
        },
    ],
}
html_context = {
    "github_user": "gee-community",
    "github_repo": "pytest-gee",
    "github_version": "main",
    "doc_path": "docs",
}
html_css_files = ["custom.css"]

# -- Options for autosummary/autodoc output ------------------------------------
autodoc_typehints = "description"
autoapi_dirs = ["../pytest_gee"]
autoapi_python_class_content = "init"
autoapi_member_order = "groupwise"

# -- Options for intersphinx output --------------------------------------------
# fmt: off
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pytest_regressions": ("https://pytest-regressions.readthedocs.io/en/latest/", None),
    "pytest": ("https://docs.pytest.org/en/stable/", None),
    "ee": ("https://developers.google.com/earth-engine/apidocs", "https://raw.githubusercontent.com/gee-community/sphinx-inventory/refs/heads/main/inventory/earthengine-api.inv"),
}
# fmt: on
