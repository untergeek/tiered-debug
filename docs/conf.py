# pylint: disable=C0103,C0114,E0401,W0611,W0622
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os

# Extract the version from the __init__.py file

path = "../src/tiered_debug/__init__.py"
myinit = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

ver = ""
with open(myinit, "r", encoding="utf-8") as file:
    lines = file.readlines()

for line in lines:
    if line.startswith("__version__"):
        ver = line.split('"')[1]

COPYRIGHT_YEARS = "2025"
# Use this starting 2026
# from datetime import datetime
# COPYRIGHT_YEARS = f"2025-{datetime.now().year}"

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath("../"))

# -- Project information -----------------------------------------------------

project = "tiered-debug"
author = "Aaron Mildenstein"
copyright = f"{COPYRIGHT_YEARS}, {author}"
release = ver
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # For Google and NumPy docstring support
    "sphinx.ext.viewcode",  # Add links to source code
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = "alabaster"
# html_static_path = ["_static"]

# -- Autodoc configuration ---------------------------------------------------

autoclass_content = "both"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

on_rtd = os.environ.get("READTHEDOCS", None) == "True"

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.12", None),
    "elasticsearch8": ("https://elasticsearch-py.readthedocs.io/en/v8.18.0", None),
    "elastic-transport": (
        "https://elastic-transport-python.readthedocs.io/en/stable",
        None,
    ),
}
