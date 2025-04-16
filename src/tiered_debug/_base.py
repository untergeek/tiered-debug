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

Each of the lv# functions can also manually override the stacklevel:

.. code-block: python
    def lv1(self, msg: str, stklvl: t.Optional[StackLevel] = self.stacklevel) -> None:

The default value of ``stklvl`` is the global ``_stacklevel`` variable, which is
set to 2 by default.

The utility is evident in the ``begin_end()`` decorator function. Since this is
a wrapper, it adds one more level of abstraction from the calling function, which
means that the stacklevel needs to be increased.
"""

# pylint: disable=C0103,W0212,W0603,W0613,W0718
import typing as t
from os import environ
import sys
from functools import wraps
import logging

DebugLevel = t.Literal[1, 2, 3, 4, 5]
StackLevel = t.Literal[1, 2, 3, 4, 5, 6, 7, 8, 9]  # probably overkill > 4

logger = logging.getLogger(__name__)

ENVVAR = "TIERED_DEBUG_LEVEL"


class TieredDebug:
    """Tiered Debug Logging Class"""

    def __init__(self, level: DebugLevel = 1, stacklevel: StackLevel = 2) -> None:
        self.level = level
        self.stacklevel = stacklevel
        self.env_level = environ.get(ENVVAR, None)
        if self.env_level is not None:
            # Check if the environment variable is set and is a valid integer
            try:
                self.level = self.check_level(int(self.env_level))
            except ValueError:
                self.level = 1

    def check_level(self, level: int) -> DebugLevel:
        """Check if the level is between 1 and 5"""
        if not 1 <= level <= 5:
            raise ValueError("Debug level must be between 1 and 5")
        return level

    def set_level(self, level: DebugLevel, override: bool = False) -> None:
        """Set :py:attr:`level` to the specified level if
        - The environment variable is not set
        - The override flag is set to True

        :param level: The debug level (1-5).
        :type level: DebugLevel
        :param override: If True, override the environment variable.
        :type override: bool
        :raises ValueError: If level is not between 1 and 5.
        """
        if self.env_level is None or override:
            # Either override is false and no envvar is set
            #   or
            # override is True
            # If either condition is true, set the level
            self.level = self.check_level(level)
        # implied else is to do nothing. self.level remains unchanged

    def set_stacklevel(self, level: StackLevel) -> None:
        """Set :py:attr:`stacklevel` to the specified level

        :param level: The stacklevel to use for the log message.
        :type level: int
        :raises ValueError: If level is not between 1 and 9.
        """
        if not 1 <= level <= 9:
            raise ValueError("stacklevel must be between 1 and 9")
        self.stacklevel = level

    def lv1(self, msg: str, stklvl: t.Optional[StackLevel] = None) -> None:
        """Log a debug message at level 1.
        :param msg: The message to log.
        :type msg: str
        :param stklvl: The stacklevel to use for the log message.
        :type stklvl: int
        """
        if stklvl is None:
            stklvl = self.stacklevel
        # No condition here because this is the default level
        # Sending stklvel - 1 here because we're already getting the calling module
        # at level 1 and stklvel defaults to 2.
        logger.name = sys._getframe(stklvl - 1).f_globals["__name__"]
        logger.debug(f"DEBUG1 {msg}", stacklevel=stklvl)

    def lv2(self, msg: str, stklvl: t.Optional[StackLevel] = None) -> None:
        """Log a debug message at level 2.
        :param msg: The message to log.
        :type msg: str
        :param stklvl: The stacklevel to use for the log message.
        :type stklvl: int
        """
        if stklvl is None:
            stklvl = self.stacklevel
        if 2 <= self.level:
            logger.name = sys._getframe(stklvl - 1).f_globals["__name__"]
            logger.debug(f"DEBUG2 {msg}", stacklevel=stklvl)

    def lv3(self, msg: str, stklvl: t.Optional[StackLevel] = None) -> None:
        """Log a debug message at level 3.
        :param msg: The message to log.
        :type msg: str
        :param stklvl: The stacklevel to use for the log message.
        :type stklvl: int
        """
        if stklvl is None:
            stklvl = self.stacklevel
        if 3 <= self.level:
            logger.name = sys._getframe(stklvl - 1).f_globals["__name__"]
            logger.debug(f"DEBUG3 {msg}", stacklevel=stklvl)

    def lv4(self, msg: str, stklvl: t.Optional[StackLevel] = None) -> None:
        """Log a debug message at level 4.
        :param msg: The message to log.
        :type msg: str
        :param stklvl: The stacklevel to use for the log message.
        :type stklvl: int
        """
        if stklvl is None:
            stklvl = self.stacklevel
        if 4 <= self.level:
            logger.name = sys._getframe(stklvl - 1).f_globals["__name__"]
            logger.debug(f"DEBUG4 {msg}", stacklevel=stklvl)

    def lv5(self, msg: str, stklvl: t.Optional[StackLevel] = None) -> None:
        """Log a debug message at level 5.
        :param msg: The message to log.
        :type msg: str
        :param stklvl: The stacklevel to use for the log message.
        :type stklvl: int
        """
        if stklvl is None:
            stklvl = self.stacklevel
        if 5 <= self.level:
            logger.name = sys._getframe(stklvl - 1).f_globals["__name__"]
            logger.debug(f"DEBUG5 {msg}", stacklevel=stklvl)


def begin_end(cls, begin: t.Optional[int] = 2, end: t.Optional[int] = 3) -> t.Callable:
    """Decorator to log the beginning and end of a function.

    This decorator will log the beginning and end of a function call at the
    specified levels, defaulting to 2 for the beginning and 3 for the ending.

    :return: The decorated function.
    :rtype: Callable
    """
    mmap = {
        1: cls.lv1,
        2: cls.lv2,
        3: cls.lv3,
        4: cls.lv4,
        5: cls.lv5,
    }

    def decorator(func: t.Callable) -> t.Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            common = f"CALL: {func.__name__}()"
            mmap[begin](f"BEGIN {common}", stklvl=cls.stacklevel + 1)
            result = func(*args, **kwargs)
            mmap[end](f"END {common}", stklvl=cls.stacklevel + 1)
            return result

        return wrapper

    return decorator
