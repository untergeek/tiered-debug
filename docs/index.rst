
tiered_debug documentation
==========================

**tiered-debug** is a Python module for tiered debug logging at levels 1-5, with
configurable stack levels for accurate caller reporting and extra metadata for
enhanced log context. It is designed for projects requiring detailed debugging,
such as Elasticsearch workflows.

The module provides a ``TieredDebug`` class for logging, and the ``debug.py``
module offers a global ``TieredDebug`` instance and a ``begin_end`` decorator to
log function entry and exit at customizable debug levels.

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
