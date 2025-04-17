"""Unit tests for the tiered_debug._base module.

This module tests the `TieredDebug` class, which provides tiered debug logging at
levels 1-5 with configurable stack levels for caller reporting. Tests cover initialization,
level and stacklevel properties, logger configuration, and logging behavior.
Designed for use in projects like ElasticKeeper and ElasticCheckpoint.

Examples:
    .. code-block:: python

        from tiered_debug._base import TieredDebug
        import logging

        debug = TieredDebug(level=2)
        debug.add_handler(logging.StreamHandler(), formatter=logging.Formatter(
            "%(asctime)s %(funcName)s:%(lineno)d %(message)s"))
        debug.lv1("Test message")  # Logs at level 1
        debug.lv3("Not logged")    # Ignored (level 3 > 2)
"""

# pylint: disable=W0212,W0621
import logging
import sys
import platform
import pytest
from tiered_debug._base import DEFAULTS, TieredDebug

BASENAME = "tiered_debug._base"
"""Module name for debug.logger"""


@pytest.fixture
def debug():
    """Create a fresh TieredDebug instance for each test.

    :return: TieredDebug instance with default settings.
    :rtype: TieredDebug
    """
    return TieredDebug()


# Tests for initialization
def test_default_initialization(debug):
    """Test default initialization values.

    Verifies that a new TieredDebug instance uses default debug and stack levels.
    """
    assert debug.level == DEFAULTS["debug"]
    assert debug.stacklevel == DEFAULTS["stack"]
    assert debug.logger.name == BASENAME


def test_custom_initialization():
    """Test initialization with custom values.

    Verifies that custom level, stacklevel, and logger_name are set correctly.
    """
    instance = TieredDebug(level=3, stacklevel=4, logger_name="custom")
    assert instance.level == 3
    assert instance.stacklevel == 4
    assert instance.logger.name == "custom"


# Tests for level property and setter
def test_level_property(debug):
    """Test that level property returns the current level."""
    debug._level = 3
    assert debug.level == 3


def test_level_setter_valid(debug):
    """Test that level setter sets level correctly for valid inputs."""
    debug.level = 1
    assert debug._level == 1
    debug.level = 3
    assert debug._level == 3
    debug.level = 5
    assert debug._level == 5


def test_level_setter_invalid(debug, caplog):
    """Test that level setter handles invalid inputs correctly."""
    with caplog.at_level(logging.WARNING, logger=debug.logger.name):
        debug.level = 0
        assert "Invalid debug level: 0" in caplog.text
        assert debug.level == DEFAULTS["debug"]

    caplog.clear()

    with caplog.at_level(logging.WARNING, logger=debug.logger.name):
        debug.level = 6
        assert "Invalid debug level: 6" in caplog.text
        assert debug.level == DEFAULTS["debug"]


# Tests for stacklevel property and setter
def test_stacklevel_property(debug):
    """Test that stacklevel property returns the current stacklevel."""
    debug._stacklevel = 3
    assert debug.stacklevel == 3


def test_stacklevel_setter_valid(debug):
    """Test that stacklevel setter sets stacklevel correctly for valid inputs."""
    debug.stacklevel = 1
    assert debug._stacklevel == 1
    debug.stacklevel = 3
    assert debug._stacklevel == 3
    debug.stacklevel = 9
    assert debug._stacklevel == 9


def test_stacklevel_setter_invalid(debug, caplog):
    """Test that stacklevel setter handles invalid inputs correctly."""
    with caplog.at_level(logging.WARNING, logger=debug.logger.name):
        debug.stacklevel = 0
        assert "Invalid stack level: 0" in caplog.text
        assert debug.stacklevel == DEFAULTS["stack"]

    caplog.clear()

    with caplog.at_level(logging.WARNING, logger=debug.logger.name):
        debug.stacklevel = 10
        assert "Invalid stack level: 10" in caplog.text
        assert debug.stacklevel == DEFAULTS["stack"]


# Tests for logger property
def test_logger_property(debug):
    """Test that logger property returns the instance-level logger."""
    assert isinstance(debug.logger, logging.Logger)
    assert debug.logger.name == BASENAME


def test_logger_custom_name():
    """Test that logger property reflects custom logger name."""
    debug = TieredDebug(logger_name="test.logger")
    assert debug.logger.name == "test.logger"


# Tests for add_handler method
def test_add_handler(debug, caplog):
    """Test that add_handler adds a handler and logs correctly."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(funcName)s:%(lineno)d %(message)s")
    debug.add_handler(handler, formatter=formatter)

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.lv1("Test message")
        assert "DEBUG1 Test message" in caplog.text
        assert handler in debug.logger.handlers


def test_add_handler_duplicate(debug, caplog):
    """Test that add_handler skips duplicate handlers with an info message."""
    handler = logging.StreamHandler()
    debug.add_handler(handler)
    post_add = len(debug.logger.handlers)

    with caplog.at_level(logging.INFO, logger=debug.logger.name):
        debug.add_handler(handler)
        assert "Handler already attached to logger, skipping" in caplog.text
        assert len(debug.logger.handlers) == post_add  # No duplicate added


# Tests for check_val method
def test_check_val_valid(debug):
    """Test that check_val returns valid values unchanged."""
    assert debug.check_val(3, "debug") == 3
    assert debug.check_val(5, "debug") == 5
    assert debug.check_val(3, "stack") == 3
    assert debug.check_val(9, "stack") == 9


def test_check_val_invalid(debug, caplog):
    """Test that check_val returns default values for invalid inputs."""
    with caplog.at_level(logging.WARNING, logger=debug.logger.name):
        assert debug.check_val(0, "debug") == DEFAULTS["debug"]
        assert "Invalid debug level: 0" in caplog.text

    caplog.clear()

    with caplog.at_level(logging.WARNING, logger=debug.logger.name):
        assert debug.check_val(10, "stack") == DEFAULTS["stack"]
        assert "Invalid stack level: 10" in caplog.text


def test_check_val_invalid_kind(debug):
    """Test that check_val raises ValueError for invalid kind."""
    with pytest.raises(ValueError, match="Invalid kind: invalid"):
        debug.check_val(3, "invalid")


# Tests for _select_frame_getter and _get_logger_name
def test_get_logger_name_valid(debug):
    """Test that _get_logger_name returns correct module name."""
    name = debug._get_logger_name(1)
    assert name == __name__


def test_get_logger_name_invalid_stack(debug):
    """Test that _get_logger_name handles invalid stack levels."""
    name = debug._get_logger_name(100)  # Too deep
    assert name == "unknown"


def test_select_frame_getter_cpython(debug, monkeypatch):
    """Test that _select_frame_getter uses sys._getframe in CPython."""
    monkeypatch.setattr(platform, "python_implementation", lambda: "CPython")
    getter = debug._select_frame_getter()
    assert getter is sys._getframe


def test_select_frame_getter_non_cpython(debug, monkeypatch):
    """Test that _select_frame_getter uses inspect.currentframe in non-CPython."""
    monkeypatch.setattr(platform, "python_implementation", lambda: "PyPy")
    getter = debug._select_frame_getter()
    frame = getter(1)
    assert frame is not None  # Returns a frame object
    assert frame.f_back is not None


# Tests for change_level context manager
def test_change_level(debug):
    """Test that change_level temporarily changes the level."""
    debug.level = 2
    assert debug.level == 2

    with debug.change_level(4):
        assert debug.level == 4

    assert debug.level == 2  # Restored


def test_change_level_with_exception(debug):
    """Test that change_level restores level despite exceptions."""
    debug.level = 2

    try:
        with debug.change_level(4):
            assert debug.level == 4
            raise RuntimeError("Test exception")
    except RuntimeError:
        pass

    assert debug.level == 2  # Restored


# Tests for log method
def test_log_valid_level(debug, caplog):
    """Test that log method logs messages at valid levels."""
    debug.level = 3
    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.log(2, "Test message", stklvl=1)
        assert "DEBUG2 Test message" in caplog.text


def test_log_invalid_level(debug):
    """Test that log method raises ValueError for invalid levels."""
    with pytest.raises(ValueError, match="Debug level must be 1-5"):
        debug.log(6, "Invalid level")


def test_log_with_default_stacklevel(debug, caplog):
    """Test that log uses default stacklevel if none provided."""
    debug.stacklevel = 3
    expected = "_pytest.python"
    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.log(1, "Test message", None)
        assert (
            caplog.records[0].name == expected
        )  # In testing, stacklevel 3 points to "_pytest.python"


def test_log_with_custom_stacklevel(debug, caplog):
    """Test that log uses provided stacklevel."""
    expected = "pluggy._callers"
    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.log(1, "Test message", 4)
        assert (
            caplog.records[0].name == expected
        )  # In testing, stacklevel 4 points to "pluggy._callers"


# Tests for logging functions
@pytest.mark.parametrize(
    "debug_level,log_level,should_log",
    [
        (1, 1, True),  # lv1 always logs
        (1, 2, False),  # lv2 shouldn't log at debug level 1
        (1, 3, False),  # lv3 shouldn't log at debug level 1
        (3, 1, True),  # lv1 always logs
        (3, 2, True),  # lv2 should log at debug level 3
        (3, 3, True),  # lv3 should log at debug level 3
        (3, 4, False),  # lv4 shouldn't log at debug level 3
        (5, 1, True),  # lv1 always logs
        (5, 5, True),  # lv5 should log at debug level 5
    ],
)
def test_log_levels(debug, caplog, debug_level, log_level, should_log):
    """Test that log functions respect the current debug level.

    :param debug: TieredDebug instance.
    :type debug: TieredDebug
    :param caplog: Pytest caplog fixture.
    :param debug_level: Debug level to set (1-5).
    :type debug_level: int
    :param log_level: Log level to test (1-5).
    :type log_level: int
    :param should_log: Whether the message should be logged.
    :type should_log: bool
    """
    debug.level = debug_level
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    log_methods = {
        1: debug.lv1,
        2: debug.lv2,
        3: debug.lv3,
        4: debug.lv4,
        5: debug.lv5,
    }

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        log_methods[log_level](f"Test message level {log_level}")
        expected = f"DEBUG{log_level} Test message level {log_level}"
        assert (expected in caplog.text) == should_log
        if should_log:
            assert caplog.records[0].name == __name__


def test_lv1_logs_unconditionally(debug, caplog):
    """Test that lv1 logs messages without checking debug level."""
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.lv1("Unconditional message")
        debug.lv2("Conditional message")  # Should not log
        assert "DEBUG1 Unconditional message" in caplog.text
        assert "DEBUG2 Conditional message" not in caplog.text
