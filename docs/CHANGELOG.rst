Changelog
=========

All notable changes to ``tiered-debug`` will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[1.2.1] - 2025-04-17
--------------------

Added
~~~~~

- Unit tests for ``debug.py`` in ``test_debug.py``.

Changed
~~~~~~~

- Fixed unit tests in ``test_base.py`` where setting the log level for caplog was required.


[1.2.0] - 2025-04-17
--------------------

Added
~~~~~

- Instance-level logger (``self._logger``) in ``TieredDebug`` for flexible configuration.
- ``add_handler`` method to attach handlers at ``logging.DEBUG`` level, with info message for duplicates.
- Cached ``_select_frame_getter`` to use ``sys._getframe`` in CPython and ``inspect.currentframe`` elsewhere.
- Sphinx autodoc docstrings for all classes and methods.
- Support for custom logger names via ``logger_name`` parameter in ``TieredDebug.__init__``.

Changed
~~~~~~~

- Removed environment variable support (``TIERED_DEBUG_LEVEL``, ``TIERED_STACK_LEVEL``).
- Updated ``check_val`` to handle ``TypeError`` and ``ValueError`` with specific error logging.
- Improved error handling and validation throughout ``TieredDebug``.

[1.1.0] - 2025-04-15
--------------------

Added
~~~~~

- Initial ``TieredDebug`` class with tiered logging levels (1-5).
- ``begin_end`` decorator in ``debug.py`` for logging function call boundaries.
- Environment variable support for setting debug and stack levels.
- Basic unit tests in ``test_base.py``.

[1.0.0] - 2025-03-31
--------------------

Added
~~~~~

- Initial release of ``tiered_debug`` module.
- ``TieredDebug`` class with module-level logger.
- Support for debug levels 1-5 and stack levels 1-9.
- ``debug.py`` sample module with global ``debug`` instance.
