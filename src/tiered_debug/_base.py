"""TieredDebug class for loggging to multiple, tiered debugging levels."""

# pylint: disable=C0103,W0212,W0603,W0613,W0718
import typing as t
import sys
from contextlib import contextmanager
from functools import lru_cache
import logging

DebugLevel = t.Literal[1, 2, 3, 4, 5]
"""Type hint for the debug level."""

StackLevel = t.Literal[1, 2, 3, 4, 5, 6, 7, 8, 9]  # probably overkill > 4
"""Type hint for the stack level."""

LevelKind = t.Literal["debug", "stack"]
"""Type hint for the debug level."""

MAXLEVELS = {"debug": 5, "stack": 9}
"""Max levels for the debug and stack levels."""

DEFAULTS = {"debug": 1, "stack": 3}
"""Default levels for the debug and stack levels."""

logger = logging.getLogger(__name__)


class TieredDebug:
    """Tiered Debug Logging Class"""

    def __init__(
        self,
        level: DebugLevel = DEFAULTS["debug"],
        stacklevel: StackLevel = DEFAULTS["stack"],
    ) -> None:
        self.level = level
        self.stacklevel = stacklevel

    @property
    def level(self) -> DebugLevel:
        """Get the current debug level."""
        return self._level

    @level.setter
    def level(self, value: DebugLevel) -> None:
        """Set :py:attr:`level` to the specified value if
        - The environment variable is not set
        - self.override is set to True

        :param value: The debug level (1-5).
        :type value: DebugLevel
        :param override: If True, override the environment variable.
        :type override: bool
        """
        self._level = self.check_val(value, "debug")

    @property
    def stacklevel(self) -> StackLevel:
        """Get the current stacklevel."""
        return self._stacklevel

    @stacklevel.setter
    def stacklevel(self, value: StackLevel) -> None:
        """Set :py:attr:`stacklevel` to the specified value

        :param value: The stacklevel to use for the log message.
        :type value: int
        """
        self._stacklevel = self.check_val(value, "stack")

    def check_val(
        self, level: t.Union[DebugLevel, StackLevel], kind: LevelKind
    ) -> t.Union[DebugLevel, StackLevel]:
        """
        Check if level is appropriate for kind. If it isn't, or is an otherwise
        invalid type, set the default value for kind.

        :param level: The debug level or stack level.
        :type level: t.Union[DebugLevel, StackLevel]
        :param kind: The kind of level to check.
        :type kind: LevelKind
        """
        try:
            if not 1 <= level <= MAXLEVELS[kind]:
                raise ValueError(
                    f"{kind} level must be between 1 and {MAXLEVELS[kind]}"
                )
        except Exception as exc:
            logger.warning(
                f'Invalid {kind} level: "{level}". Setting to {DEFAULTS[kind]}'
            )
            logger.debug(f"Exception: {exc}")
            level = DEFAULTS[kind]
        return level

    @lru_cache(maxsize=128)
    def _get_logger_name(self, level: StackLevel) -> str:
        """Get the logger name for the specified stack level."""
        try:
            return sys._getframe(level).f_globals["__name__"]
        except (ValueError, AttributeError, KeyError):
            return "unknown"

    @contextmanager
    def change_level(self, level: DebugLevel) -> t.Generator[None, None, None]:
        """Temporarily change the debug level within a context.

        Usage:
            with debug.level_context(3):
                # Debug level is 3 here
            # Debug level is restored here
        """
        original_level = self.level
        self.level = level
        try:
            yield
        finally:
            self.level = original_level

    def log(self, level: DebugLevel, msg: str, stklvl: StackLevel) -> None:
        """Log a debug message at the specified level.
        :param msg: The message to log.
        :type msg: str
        :param stklvl: The stacklevel to use for the log message.
        :type stklvl: int
        """
        if stklvl is None:
            stklvl = self.stacklevel
        # Only log if the level is less than or equal to the current level
        if level == 1 or level <= self.level:
            logger.name = self._get_logger_name(stklvl)
            logger.debug(f"DEBUG{level} {msg}", stacklevel=stklvl)

    def lv1(self, msg: str, stklvl: t.Optional[StackLevel] = None) -> None:
        """Log a level 1 debug message."""
        self.log(1, msg, stklvl=stklvl)

    def lv2(self, msg: str, stklvl: t.Optional[StackLevel] = None) -> None:
        """Log a level 2 debug message."""
        self.log(2, msg, stklvl=stklvl)

    def lv3(self, msg: str, stklvl: t.Optional[StackLevel] = None) -> None:
        """Log a level 3 debug message."""
        self.log(3, msg, stklvl=stklvl)

    def lv4(self, msg: str, stklvl: t.Optional[StackLevel] = None) -> None:
        """Log a level 4 debug message."""
        self.log(4, msg, stklvl=stklvl)

    def lv5(self, msg: str, stklvl: t.Optional[StackLevel] = None) -> None:
        """Log a level 5 debug message."""
        self.log(5, msg, stklvl=stklvl)
