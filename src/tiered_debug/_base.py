"""Module with functions to log to multiple tiered debugging levels.

This module provides a way to enable multiple tiers of debug logging. It's not
doing anything fancy, just a wrapper around a standard ``logger.debug()``
call that caps the highest tier of debug logging to the value of ``_level``
which can be set via the environment variable ``TIERED_DEBUG_LEVEL`` at runtime,
with a built-in default of 1. It can be set to a value between 1 and 5. It can
also be set interactively via the ``set_level()`` function.


For example:

.. code-block: python
    import tiered_debugging as debug

    # Set the debug level globally (optional if using environment variable)
    debug.set_level(3)

    # Log messages from any module
    debug.lv1("This will log")  # Logs because 1 <= 3
    debug.lv3("This will log")  # Logs because 3 <= 3
    debug.lv4("This won't log") # Doesn't log because 4 > 3


The ``stacklevel`` parameter is passed to the :py:func:`logging.debug()` function
as the `stacklevel` argument. The ``stacklevel`` parameter is the stack level to
use for the log message. The default value is 2, which means that the log message
will appear to come from the caller of the caller each ``lv#`` function. In other
words, if you call ``lv1()`` from a function, the log message will appear to
come from the caller of that function. If your log formatter is set up to include
the module name, function name, and/or line of code in the log message, having the
stacklevel properly set will ensure the correct data is displayed.

In the event that you use this module as part of another module or class, you may
need to increase the ``stacklevel`` to 3. This can be done using the
``set_stacklevel()`` function. This will need to be done before any logging takes
place.
"""

# pylint: disable=C0103,W0603
import typing as t
from os import environ
import logging

DebugLevel = t.Literal[1, 2, 3, 4, 5]

logger = logging.getLogger(__name__)

ENVVAR = "TIERED_DEBUG_LEVEL"

# Initialize global variables _level and _stacklevel
_level = 1
_stacklevel = 2

# Check if the environment variable is set and is a valid integer
env_level = environ.get(ENVVAR)
if env_level is not None:
    try:
        _level = int(env_level)
        if not 1 <= _level <= 5:
            _level = 1
    except ValueError:
        _level = 1


def set_level(level: DebugLevel) -> None:
    """Set the global value for _level.

    :param level: The debug level (1-5).
    :type level: DebugLevel
    :raises ValueError: If level is not between 1 and 5.
    """
    global _level
    if not 1 <= level <= 5:
        raise ValueError("Debug level must be between 1 and 5")
    _level = level


def set_stacklevel(level: int) -> None:
    """Set the global value for _stacklevel.

    :param level: The stacklevel to use for the log message.
    :type level: int
    :raises ValueError: If level is not between 1 and 3.
    """
    global _stacklevel
    if not 1 <= level <= 3:
        raise ValueError("stacklevel must be between 1 and 3")
    _stacklevel = level


def lv1(msg: str) -> None:
    """Log a debug message at level 1."""
    # No condition here because this is the default level
    logger.debug(f"DEBUG1 {msg}", stacklevel=2)


def lv2(msg: str) -> None:
    """Log a debug message at level 2."""
    if 2 <= _level:
        logger.debug(f"DEBUG2 {msg}", stacklevel=2)


def lv3(msg: str) -> None:
    """Log a debug message at level 3."""
    if 3 <= _level:
        logger.debug(f"DEBUG3 {msg}", stacklevel=2)


def lv4(msg: str) -> None:
    """Log a debug message at level 4."""
    if 4 <= _level:
        logger.debug(f"DEBUG4 {msg}", stacklevel=2)


def lv5(msg: str) -> None:
    """Log a debug message at level 5."""
    if 5 <= _level:
        logger.debug(f"DEBUG5 {msg}", stacklevel=2)
