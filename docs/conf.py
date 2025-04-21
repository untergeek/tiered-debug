"""Sphinx configuration for tiered-debug documentation.

Configures Sphinx to generate documentation for the tiered-debug package,
using autodoc, Napoleon, doctest, viewcode, and intersphinx extensions.
Imports metadata (__version__, __author__, __copyright__) from
tiered_debug, leveraging module installation for ReadTheDocs. Sets up
GitHub integration for "Edit Source" links and supports Python 3.8-3.13.

Attributes:
    project: Project name ("tiered-debug"). (str)
    author: Author name from tiered_debug.__author__. (str)
    version: Major.minor version (e.g., "1.3"). (str)
    release: Full version (e.g., "1.3.0"). (str)
    html_theme: Theme for HTML output, defaults to "sphinx_rtd_theme". (str)

Examples:
    >>> project
    'tiered-debug'
    >>> author
    'Aaron Mildenstein'
    >>> version
    '1.3'
    >>> 'autodoc' in [ext.split('.')[-1] for ext in extensions]
    True
"""

# pylint: disable=C0103,E0401,W0622

# -- Imports and setup -----------------------------------------------------
from os import environ
from tiered_debug import __author__, __copyright__, __version__

# -- Project information -----------------------------------------------------

project = "tiered-debug"
github_user = "untergeek"
github_repo = "tiered-debug"
github_branch = "main"
author = __author__
copyright = __copyright__
release = __version__
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
]
napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ["_templates"]
exclude_patterns = ["_build"]
source_suffix = ".rst"
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

pygments_style = "sphinx"
html_theme = "sphinx_rtd_theme" if environ.get("READTHEDOCS") != "True" else None

# Add "Edit Source" links into the template
html_context = {
    "display_github": True,
    "github_user": github_user,
    "github_repo": github_repo,
    "github_version": github_branch,
    "conf_py_path": "/docs/",
}

# -- Autodoc configuration ---------------------------------------------------

autoclass_content = "both"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# -- Intersphinx configuration -----------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.12", None),
}
