"""Tiered debug logging for multiple levels with stack tracing.

This module provides the `TieredDebug` class for logging debug messages at tiered
levels (1-5), with configurable stack levels for accurate function and line number
reporting. It is designed for use in projects like ElasticKeeper and ElasticCheckpoint,
integrating with Elasticsearch logging workflows. The debug level and stack level are
set via constructor arguments or defaults. The logger is instance-level, allowing
custom handlers (e.g., Elasticsearch) to be added via `add_handler`.

.. note::
    Configure the logger with `add_handler` to include fields like ``%(funcName)s`` and
    ``%(lineno)d`` for full compatibility with testing frameworks like pytest's caplog.
"""

# pylint: disable=W0212
import logging
import sys
import inspect
import platform
from typing import Callable, Generator, Literal, Optional, Union, TYPE_CHECKING
from functools import lru_cache
from contextlib import contextmanager

if TYPE_CHECKING:
    from types import FrameType


DebugLevel = Literal[1, 2, 3, 4, 5]
"""Type hint for debug level (1-5)."""

StackLevel = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9]
"""Type hint for stack level (1-9)."""

LevelKind = Literal["debug", "stack"]
"""Type hint for level kind."""

MAXLEVELS = {"debug": 5, "stack": 9}
"""Maximum levels for debug and stack."""

DEFAULTS = {"debug": 1, "stack": 3}
"""Default levels for debug and stack."""


class TieredDebug:
    """Tiered debug logging class for configurable, multi-level debugging.

    This class manages debug logging at levels 1-5, with adjustable stack levels
    to report the caller's function and line number. It is suitable for projects
    requiring detailed debugging, such as Elasticsearch workflows. The logger is
    an instance variable, configurable via `add_handler`.

    :ivar level: Current debug level (1-5), controlling which messages are logged.
    :ivar stacklevel: Stack level (1-9) for reporting caller function and line number.
    :ivar logger: The instance-level logger for debug messages.

    Examples:
        .. code-block:: python

            debug = TieredDebug()
            debug.add_handler(logging.StreamHandler(), formatter=logging.Formatter(
                "%(asctime)s %(funcName)s:%(lineno)d %(message)s"))
            debug.lv1("Level 1 message")  # Logs with default stacklevel=3
            debug.level = 4
            debug.lv4("Level 4 message")  # Logs
            debug.lv5("Level 5 message")  # Ignored
    """

    def __init__(
        self,
        level: Optional[DebugLevel] = None,
        stacklevel: Optional[StackLevel] = None,
        logger_name: Optional[str] = None,
    ) -> None:
        """Initialize TieredDebug with optional level, stacklevel, and logger name.

        :param level: Debug level (1-5). Defaults to 1.
        :type level: Optional[DebugLevel]
        :param stacklevel: Stack level (1-9). Defaults to 3.
        :type stacklevel: Optional[StackLevel]
        :param logger_name: Name for the logger. Defaults to module name.
        :type logger_name: Optional[str]
        """
        self._level = self.check_val(level or DEFAULTS["debug"], "debug")
        self._stacklevel = self.check_val(stacklevel or DEFAULTS["stack"], "stack")
        self._logger = logging.getLogger(logger_name or __name__)

    @property
    def level(self) -> DebugLevel:
        """Get the current debug level.

        :return: The current debug level (1-5).
        :rtype: DebugLevel
        """
        return self._level

    @level.setter
    def level(self, value: DebugLevel) -> None:
        """Set the debug level, validating the input.

        :param value: Debug level (1-5).
        :type value: DebugLevel
        :raises ValueError: If value is not a valid debug level.
        """
        self._level = self.check_val(value, "debug")

    @property
    def stacklevel(self) -> StackLevel:
        """Get the current stack level.

        :return: The current stack level (1-9).
        :rtype: StackLevel
        """
        return self._stacklevel

    @stacklevel.setter
    def stacklevel(self, value: StackLevel) -> None:
        """Set the stack level, validating the input.

        :param value: Stack level (1-9).
        :type value: StackLevel
        :raises ValueError: If value is not a valid stack level.
        """
        self._stacklevel = self.check_val(value, "stack")

    @property
    def logger(self) -> logging.Logger:
        """Get the instance-level logger.

        :return: The logger used for debug messages.
        :rtype: logging.Logger
        """
        return self._logger

    def check_val(
        self, level: Union[DebugLevel, StackLevel], kind: LevelKind
    ) -> Union[DebugLevel, StackLevel]:
        """Validate a level for the given kind (debug or stack).

        :param level: Debug or stack level to validate.
        :type level: Union[DebugLevel, StackLevel]
        :param kind: Type of level ("debug" or "stack").
        :type kind: LevelKind
        :return: Validated level, or default if invalid.
        :rtype: Union[DebugLevel, StackLevel]
        :raises ValueError: If kind is invalid or level is out of range.
        """
        if kind not in MAXLEVELS:
            raise ValueError(f"Invalid kind: {kind}. Must be 'debug' or 'stack'")

        try:
            level = int(level)  # Ensure level is an integer
            if not 1 <= level <= MAXLEVELS[kind]:
                raise ValueError(
                    f"{kind} level must be between 1 and {MAXLEVELS[kind]}"
                )
        except (TypeError, ValueError) as exc:
            self._logger.warning(
                f"Invalid {kind} level: {level} ({type(exc).__name__}). "
                f"Using default: {DEFAULTS[kind]}"
            )
            level = DEFAULTS[kind]
        return level  # type: ignore

    def add_handler(
        self, handler: logging.Handler, formatter: Optional[logging.Formatter] = None
    ) -> None:
        """Add a handler to the instance logger at DEBUG level.

        If the handler is already attached, logs an info message and skips adding it.

        :param handler: Handler to add (e.g., StreamHandler, FileHandler).
        :type handler: logging.Handler
        :param formatter: Formatter for the handler. Optional.
        :type formatter: Optional[logging.Formatter]
        """
        if handler in self._logger.handlers:
            self._logger.info("Handler already attached to logger, skipping")
            return
        handler.setLevel(logging.DEBUG)
        if formatter is not None:
            handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    @lru_cache(maxsize=1)
    def _select_frame_getter(self) -> Callable[[int], "FrameType"]:
        """Select the frame getter function based on Python implementation.

        :return: Function to get a stack frame (sys._getframe or inspect.currentframe).
        :rtype: Callable[[int], FrameType]
        """
        if platform.python_implementation() == "CPython":
            return sys._getframe
        return lambda level: (
            inspect.currentframe().f_back
            if level == 1
            else inspect.currentframe().f_back.f_back
        )

    def _get_logger_name(self, level: StackLevel) -> str:
        """Get the logger name for the specified stack level.

        :param level: Stack level to inspect.
        :type level: StackLevel
        :return: Module name at the specified stack level, or 'unknown' if not found.
        :rtype: str
        """
        try:
            frame_getter = self._select_frame_getter()
            frame = frame_getter(level)
            return frame.f_globals["__name__"]
        except (ValueError, AttributeError, KeyError):
            return "unknown"

    @contextmanager
    def change_level(self, level: DebugLevel) -> Generator[None, None, None]:
        """Temporarily change the debug level within a context.

        :param level: Debug level to set temporarily.
        :type level: DebugLevel
        :yields: None
        :rtype: contextlib._GeneratorContextManager[None]

        Examples:
            .. code-block:: python

                debug = TieredDebug(level=2)
                with debug.change_level(4):
                    debug.lv4("This will log")  # Logs
                debug.lv4("This won't log")  # Ignored
        """
        original_level = self.level
        self.level = level
        try:
            yield
        finally:
            self.level = original_level

    def log(
        self, level: DebugLevel, msg: str, stklvl: Optional[StackLevel] = None
    ) -> None:
        """Log a debug message at the specified level.

        :param level: Debug level (1-5) for the message.
        :type level: DebugLevel
        :param msg: Message to log.
        :type msg: str
        :param stklvl: Stack level for caller reporting (defaults to instance stacklevel).
        :type stklvl: Optional[StackLevel]
        :raises ValueError: If level is invalid.
        """
        if level not in (1, 2, 3, 4, 5):
            raise ValueError("Debug level must be 1-5")
        stklvl = stklvl if stklvl is not None else self.stacklevel
        if level <= self.level:
            self._logger.name = self._get_logger_name(stklvl)
            self._logger.debug(f"DEBUG{level} {msg}", stacklevel=stklvl)

    def lv1(self, msg: str, stklvl: Optional[StackLevel] = None) -> None:
        """Log a level 1 debug message.

        :param msg: Message to log.
        :type msg: str
        :param stklvl: Stack level for caller reporting (optional).
        :type stklvl: Optional[StackLevel]
        """
        self.log(1, msg, stklvl)

    def lv2(self, msg: str, stklvl: Optional[StackLevel] = None) -> None:
        """Log a level 2 debug message.

        :param msg: Message to log.
        :type msg: str
        :param stklvl: Stack level for caller reporting (optional).
        :type stklvl: Optional[StackLevel]
        """
        self.log(2, msg, stklvl)

    def lv3(self, msg: str, stklvl: Optional[StackLevel] = None) -> None:
        """Log a level 3 debug message.

        :param msg: Message to log.
        :type msg: str
        :param stklvl: Stack level for caller reporting (optional).
        :type stklvl: Optional[StackLevel]
        """
        self.log(3, msg, stklvl)

    def lv4(self, msg: str, stklvl: Optional[StackLevel] = None) -> None:
        """Log a level 4 debug message.

        :param msg: Message to log.
        :type msg: str
        :param stklvl: Stack level for caller reporting (optional).
        :type stklvl: Optional[StackLevel]
        """
        self.log(4, msg, stklvl)

    def lv5(self, msg: str, stklvl: Optional[StackLevel] = None) -> None:
        """Log a level 5 debug message.

        :param msg: Message to log.
        :type msg: str
        :param stklvl: Stack level for caller reporting (optional).
        :type stklvl: Optional[StackLevel]
        """
        self.log(5, msg, stklvl)
