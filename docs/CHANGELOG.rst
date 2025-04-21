Changelog
=========

All notable changes to ``tiered-debug`` will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[1.3.0] - 2025-04-21
--------------------

Added
~~~~~

- Added ``exc_info``, ``stack_info``, and ``extra`` keyword arguments to ``log``, ``lv1``, ``lv2``, ``lv3``, ``lv4``, and ``lv5`` methods in ``TieredDebug``, following Python ``logging`` module specifications.
- ``log`` method now ensures ``extra`` is an empty dictionary if ``None`` is provided.
- Standardized all docstrings in ``_base.py`` to Google-style format with line length limits (code and docstrings: soft 80, hard 88; Args/Returns/Raises definitions: soft 72, hard 80; Examples: soft 68, hard 76).
- Added doctests to ``_base.py`` for key methods to demonstrate usage and validate behavior.
- Standardized all docstrings in ``debug.py`` to Google-style format with line length limits (code and docstrings: soft 80, hard 88; Args/Returns/Raises definitions: soft 72, hard 80; Examples: soft 68, hard 76).
- Added doctests to ``debug.py`` with line length limits (soft 68, hard 76) for decorator and global instance.
- Standardized module docstring in ``__init__.py`` to Google-style format with doctests and line length limits (code and docstrings: soft 80, hard 88; Args/Returns/Raises definitions: soft 72, hard 80; Examples: soft 68, hard 76).
- Updated ``docs/conf.py`` for tiered-debug with Google-style docstring, doctests, direct metadata imports enabled by module installation, and line length limits (code and docstrings: soft 80, hard 88; Args/Returns/Raises definitions: soft 72, hard 80; Examples: soft 68, hard 76).
- Updated ``.readthedocs.yaml`` to configure ReadTheDocs build with module installation, Sphinx configuration, and dependency installation via ``docs/requirements.txt``.
- Added ``docs/requirements.txt`` with Sphinx dependencies for ReadTheDocs documentation builds.
- Enhanced tests in ``test_base.py`` to cover ``exc_info``, ``stack_info``, and ``extra`` parameters in ``TieredDebug`` logging methods, including edge cases and performance.
- Added ``__version__``, ``__author__``, and ``__copyright__`` to ``__all__`` in ``__init__.py`` to export metadata.
- Added ``W0622`` to pylint disable in ``docs/conf.py`` to suppress redefined built-in warnings for ``copyright``.
- Fixed ``test_log_with_extra`` and ``test_log_all_parameters_combined`` in ``test_base.py`` to check log record attributes for ``extra`` metadata due to ``pytest.ini`` log format.
- Fixed ``test_log_with_stack_info`` and ``test_log_all_parameters_combined`` in ``test_base.py`` to check for correct stack trace prefix across Python 3.8-3.13.
- Updated ``test_log_with_invalid_extra_type`` in ``test_base.py`` to expect TypeError for invalid ``extra`` types, aligning with ``_base.py`` validation.
- Renamed ``stklvl`` to ``stacklevel`` and reordered keyword arguments (``exc_info``, ``stack_info``, ``stacklevel``, ``extra``) in ``_base.py`` methods to match ``logging.Logger.debug``.
- Updated ``debug.py`` to use ``stacklevel`` and enhanced ``begin_end`` decorator to accept ``stacklevel`` and ``extra``, defaulting to updating only ``stacklevel``.
- Updated ``test_base.py`` to use ``stacklevel``, reordered keyword arguments, and added tests for ``*args`` message formatting support in ``_base.py`` methods.
- Fixed ``test_select_frame_getter_non_cpython`` in ``test_base.py`` to correctly call ``inspect.currentframe()`` without arguments.
- Updated ``debug.py`` to restore ``begin`` and ``end`` arguments for ``begin_end`` decorator, retaining ``stacklevel`` and ``extra``.
- Updated ``test_debug.py`` to test ``begin``, ``end``, ``stacklevel``, and ``extra`` in ``begin_end`` decorator, restoring original test structure.
- Corrected ``test_debug.py`` to ensure all tests pass, as updated by user.
- Updated ``index.rst`` to highlight ``stacklevel`` and ``extra`` and clarify ``debug.py``’s role.
- Updated ``usage.rst`` to include ``stacklevel``, ``extra``, ``*args``, correct ``set_level``, align log output with ``pytest.ini``, and enhance Elasticsearch handler example.
- Updated ``usage.rst`` formatters to include ``extra`` fields (``%(context)s``, ``%(module)s``) in log output for ``TieredDebug``, ``debug.py``, Elasticsearch, and pytest examples.
- Re-rendered ``usage.rst`` Python code blocks to fit within a 90-character hard limit to avoid side-scrolling.
- Corrected spacing in ``usage.rst`` bash code block to improve visibility in rendered documentation, as updated by user.

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
