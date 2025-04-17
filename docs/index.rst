
tiered_debug documentation
==========================

**tiered-debug** is a Python module for tiered debug logging at levels 1-5, with
configurable stack levels for accurate function and line number reporting. It is
designed for projects desiring detailed debugging.

The module provides a ``TieredDebug`` class for logging and sample ``debug.py`` module
demonstrates how to set up a global ``TieredDebug`` instance for project-wide use,
complete with a ``begin_end`` decorator for tracking function call boundaries.  

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   debug
   api
   contributing
   CHANGELOG

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
