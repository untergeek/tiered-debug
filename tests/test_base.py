"""Unit tests for the tiered_debug._base module.

Tests the `TieredDebug` class, which provides tiered debug logging at
levels 1-5 with configurable stack levels for caller reporting. Covers
initialization, level and stacklevel properties, logger configuration,
logging behavior, and parameters (`exc_info`, `stack_info`, `stacklevel`,
`extra`). Designed for use in projects like ElasticKeeper and
ElasticCheckpoint.

Examples:
    >>> from tiered_debug._base import TieredDebug
    >>> import logging
    >>> debug = TieredDebug(level=2)
    >>> handler = logging.StreamHandler()
    >>> debug.add_handler(handler, logging.Formatter("%(message)s"))
    >>> debug.lv1("Test message: %s", "value")  # Logs at level 1
    >>> debug.lv3("Not logged")  # Ignored (level 3 > 2)
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

    Returns:
        TieredDebug: Instance with default settings.

    Examples:
        >>> debug = TieredDebug()
        >>> isinstance(debug, TieredDebug)
        True
    """
    return TieredDebug()


# Tests for initialization
def test_default_initialization(debug):
    """Test default initialization values.

    Verifies that a new TieredDebug instance uses default debug and stack
    levels.

    Examples:
        >>> debug = TieredDebug()
        >>> debug.level
        1
        >>> debug.stacklevel
        3
    """
    assert debug.level == DEFAULTS["debug"]
    assert debug.stacklevel == DEFAULTS["stack"]
    assert debug.logger.name == BASENAME


def test_custom_initialization():
    """Test initialization with custom values.

    Verifies that custom level, stacklevel, and logger_name are set
    correctly.

    Examples:
        >>> debug = TieredDebug(level=3, stacklevel=4, logger_name="custom")
        >>> debug.level
        3
        >>> debug.stacklevel
        4
        >>> debug.logger.name
        'custom'
    """
    instance = TieredDebug(level=3, stacklevel=4, logger_name="custom")
    assert instance.level == 3
    assert instance.stacklevel == 4
    assert instance.logger.name == "custom"


# Tests for level property and setter
def test_level_property(debug):
    """Test that level property returns the current level.

    Examples:
        >>> debug = TieredDebug()
        >>> debug._level = 3
        >>> debug.level
        3
    """
    debug._level = 3
    assert debug.level == 3


def test_level_setter_valid(debug):
    """Test that level setter sets level correctly for valid inputs.

    Examples:
        >>> debug = TieredDebug()
        >>> debug.level = 3
        >>> debug.level
        3
    """
    debug.level = 1
    assert debug._level == 1
    debug.level = 3
    assert debug._level == 3
    debug.level = 5
    assert debug._level == 5


def test_level_setter_invalid(debug, caplog):
    """Test that level setter handles invalid inputs correctly.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug()
        >>> debug.level = 0  # Logs warning, uses default
        >>> debug.level
        1
    """
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
    """Test that stacklevel property returns the current stacklevel.

    Examples:
        >>> debug = TieredDebug()
        >>> debug._stacklevel = 3
        >>> debug.stacklevel
        3
    """
    debug._stacklevel = 3
    assert debug.stacklevel == 3


def test_stacklevel_setter_valid(debug):
    """Test that stacklevel setter sets stacklevel correctly for valid inputs.

    Examples:
        >>> debug = TieredDebug()
        >>> debug.stacklevel = 3
        >>> debug.stacklevel
        3
    """
    debug.stacklevel = 1
    assert debug._stacklevel == 1
    debug.stacklevel = 3
    assert debug._stacklevel == 3
    debug.stacklevel = 9
    assert debug._stacklevel == 9


def test_stacklevel_setter_invalid(debug, caplog):
    """Test that stacklevel setter handles invalid inputs correctly.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug()
        >>> debug.stacklevel = 0  # Logs warning, uses default
        >>> debug.stacklevel
        3
    """
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
    """Test that logger property returns the instance-level logger.

    Examples:
        >>> debug = TieredDebug()
        >>> isinstance(debug.logger, logging.Logger)
        True
    """
    assert isinstance(debug.logger, logging.Logger)
    assert debug.logger.name == BASENAME


def test_logger_custom_name():
    """Test that logger property reflects custom logger name.

    Examples:
        >>> debug = TieredDebug(logger_name="test.logger")
        >>> debug.logger.name
        'test.logger'
    """
    debug = TieredDebug(logger_name="test.logger")
    assert debug.logger.name == "test.logger"


# Tests for add_handler method
def test_add_handler(debug, caplog):
    """Test that add_handler adds a handler and logs correctly.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug()
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> handler in debug.logger.handlers
        True
    """
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(funcName)s:%(lineno)d %(message)s")
    debug.add_handler(handler, formatter=formatter)

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.lv1("Test message")
        assert "DEBUG1 Test message" in caplog.text
        assert handler in debug.logger.handlers


def test_add_handler_duplicate(debug, caplog):
    """Test that add_handler skips duplicate handlers with an info message.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug()
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.add_handler(handler)  # Logs info, skips
    """
    caplog.set_level(logging.DEBUG)
    handler = logging.StreamHandler()
    debug.add_handler(handler)
    post_add = len(debug.logger.handlers)

    with caplog.at_level(logging.INFO, logger=debug.logger.name):
        debug.add_handler(handler)
        assert "Handler already attached to logger, skipping" in caplog.text
        assert len(debug.logger.handlers) == post_add  # No duplicate added


# Tests for check_val method
def test_check_val_valid(debug):
    """Test that check_val returns valid values unchanged.

    Args:
        debug: TieredDebug instance. (TieredDebug)

    Examples:
        >>> debug = TieredDebug()
        >>> debug.check_val(3, "debug")
        3
    """
    assert debug.check_val(3, "debug") == 3
    assert debug.check_val(5, "debug") == 5
    assert debug.check_val(3, "stack") == 3
    assert debug.check_val(9, "stack") == 9


def test_check_val_invalid(debug, caplog):
    """Test that check_val returns default values for invalid inputs.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug()
        >>> debug.check_val(0, "debug")  # Logs warning
        1
    """
    with caplog.at_level(logging.WARNING, logger=debug.logger.name):
        assert debug.check_val(0, "debug") == DEFAULTS["debug"]
        assert "Invalid debug level: 0" in caplog.text

    caplog.clear()

    with caplog.at_level(logging.WARNING, logger=debug.logger.name):
        assert debug.check_val(10, "stack") == DEFAULTS["stack"]
        assert "Invalid stack level: 10" in caplog.text


def test_check_val_invalid_kind(debug):
    """Test that check_val raises ValueError for invalid kind.

    Args:
        debug: TieredDebug instance. (TieredDebug)

    Examples:
        >>> debug = TieredDebug()
        >>> try:
        ...     debug.check_val(3, "invalid")
        ... except ValueError as e:
        ...     print(str(e))
        Invalid kind: invalid. Must be 'debug' or 'stack'
    """
    with pytest.raises(ValueError, match="Invalid kind: invalid"):
        debug.check_val(3, "invalid")


# Tests for _select_frame_getter and _get_logger_name
def test_get_logger_name_valid(debug):
    """Test that _get_logger_name returns correct module name.

    Args:
        debug: TieredDebug instance. (TieredDebug)

    Examples:
        >>> debug = TieredDebug()
        >>> debug._get_logger_name(1)
        '__main__'
    """
    name = debug._get_logger_name(1)
    assert name == __name__


def test_get_logger_name_invalid_stack(debug):
    """Test that _get_logger_name handles invalid stack levels.

    Args:
        debug: TieredDebug instance. (TieredDebug)

    Examples:
        >>> debug = TieredDebug()
        >>> debug._get_logger_name(100)
        'unknown'
    """
    name = debug._get_logger_name(100)  # Too deep
    assert name == "unknown"


def test_select_frame_getter_cpython(debug, monkeypatch):
    """Test that _select_frame_getter uses sys._getframe in CPython.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        monkeypatch: Pytest monkeypatch fixture.

    Examples:
        >>> debug = TieredDebug()
        >>> import platform
        >>> if platform.python_implementation() == "CPython":
        ...     assert debug._select_frame_getter() is sys._getframe
    """
    monkeypatch.setattr(platform, "python_implementation", lambda: "CPython")
    getter = debug._select_frame_getter()
    assert getter is sys._getframe


def test_select_frame_getter_non_cpython(debug, monkeypatch):
    """Test that _select_frame_getter uses inspect.currentframe in non-CPython.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        monkeypatch: Pytest monkeypatch fixture.

    Examples:
        >>> debug = TieredDebug()
        >>> import platform
        >>> import inspect
        >>> if platform.python_implementation() != "CPython":
        ...     frame = debug._select_frame_getter()()
        ...     assert frame is not None
    """
    monkeypatch.setattr(platform, "python_implementation", lambda: "PyPy")
    getter = debug._select_frame_getter()
    frame = getter()
    assert frame is not None  # Returns a frame object
    assert frame.f_back is not None  # Can access parent frame


# Tests for change_level context manager
def test_change_level(debug):
    """Test that change_level temporarily changes the level.

    Args:
        debug: TieredDebug instance. (TieredDebug)

    Examples:
        >>> debug = TieredDebug(level=2)
        >>> with debug.change_level(4):
        ...     assert debug.level == 4
        >>> debug.level
        2
    """
    debug.level = 2
    assert debug.level == 2

    with debug.change_level(4):
        assert debug.level == 4

    assert debug.level == 2  # Restored


def test_change_level_with_exception(debug):
    """Test that change_level restores level despite exceptions.

    Args:
        debug: TieredDebug instance. (TieredDebug)

    Examples:
        >>> debug = TieredDebug(level=2)
        >>> try:
        ...     with debug.change_level(4):
        ...         raise RuntimeError
        ... except RuntimeError:
        ...     pass
        >>> debug.level
        2
    """
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
    """Test that log method logs messages at valid levels with args.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=3)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.log(2, "Test: %s", "value")
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 3
    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.log(2, "Test message: %s", "value", stacklevel=1)
        assert "DEBUG2 Test message: value" in caplog.text


def test_log_invalid_level(debug):
    """Test that log method raises ValueError for invalid levels.

    Args:
        debug: TieredDebug instance. (TieredDebug)

    Examples:
        >>> debug = TieredDebug()
        >>> try:
        ...     debug.log(6, "Invalid")
        ... except ValueError as e:
        ...     print(str(e))
        Debug level must be 1-5
    """
    with pytest.raises(ValueError, match="Debug level must be 1-5"):
        debug.log(6, "Invalid level")


def test_log_with_default_stacklevel(debug, caplog):
    """Test that log uses default stacklevel if none provided.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug()
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.log(1, "Test: %s", "value")
    """
    debug.stacklevel = 3
    expected = "_pytest.python"
    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.log(1, "Test message: %s", "value")
        assert (
            caplog.records[0].name == expected
        )  # In testing, stacklevel 3 points to "_pytest.python"


def test_log_with_custom_stacklevel(debug, caplog):
    """Test that log uses provided stacklevel.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug()
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.log(1, "Test: %s", "value", stacklevel=4)
    """
    caplog.set_level(logging.DEBUG)
    expected = "pluggy._callers"
    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.log(1, "Test message: %s", "value", stacklevel=4)
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

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.
        debug_level: Debug level to set (1-5). (int)
        log_level: Log level to test (1-5). (int)
        should_log: Whether the message should be logged. (bool)

    Examples:
        >>> debug = TieredDebug(level=3)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.lv2("Test: %s", "value")  # Should log
        >>> debug.lv4("Test")  # Should not log
    """
    caplog.set_level(logging.DEBUG)
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
        log_methods[log_level](f"Test message level {log_level}: %s", "value")
        expected = f"DEBUG{log_level} Test message level {log_level}: value"
        assert (expected in caplog.text) == should_log
        if should_log:
            assert caplog.records[0].name == __name__


def test_lv1_logs_unconditionally(debug, caplog):
    """Test that lv1 logs messages without checking debug level.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.lv1("Test: %s", "value")
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.lv1("Unconditional message: %s", "value")
        debug.lv2("Conditional message")
        assert "DEBUG1 Unconditional message: value" in caplog.text
        assert "DEBUG2 Conditional message" not in caplog.text


# Tests for exc_info, stack_info, and extra parameters
def test_log_with_exc_info(debug, caplog):
    """Test that log method includes exception info when exc_info=True.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> try:
        ...     raise ValueError("Test")
        ... except ValueError:
        ...     debug.lv1("Error: %s", "info", exc_info=True)
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        try:
            raise ValueError("Test error")
        except ValueError:
            debug.lv1("Error occurred: %s", "info", exc_info=True)
        assert "DEBUG1 Error occurred: info" in caplog.text
        assert "ValueError: Test error" in caplog.text


def test_log_without_exc_info(debug, caplog):
    """Test that log method excludes exception info when exc_info=False.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> try:
        ...     raise ValueError("Test")
        ... except ValueError:
        ...     debug.lv1("Error: %s", "info", exc_info=False)
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        try:
            raise ValueError("Test error")
        except ValueError:
            debug.lv1("Error occurred: %s", "info", exc_info=False)
        assert "DEBUG1 Error occurred: info" in caplog.text
        assert "ValueError: Test error" not in caplog.text


def test_log_with_stack_info(debug, caplog):
    """Test that log method includes stack info when stack_info=True.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.lv1("Test: %s", "value", stack_info=True)
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.lv1("Stack info test: %s", "value", stack_info=True)
        assert "DEBUG1 Stack info test: value" in caplog.text
        assert "Stack (most recent call last):" in caplog.text


def test_log_without_stack_info(debug, caplog):
    """Test that log method excludes stack info when stack_info=False.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.lv1("Test: %s", "value", stack_info=False)
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.lv1("No stack info test: %s", "value", stack_info=False)
        assert "DEBUG1 No stack info test: value" in caplog.text
        assert "Stack (most recent call last):" not in caplog.text


def test_log_with_extra(debug, caplog):
    """Test that log method includes extra metadata when provided.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.lv1("Test: %s", "value", extra={"custom": "value"})
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.lv1(
            "Extra test: %s",
            "value",
            extra={"custom": "custom_value"},
        )
        assert "DEBUG1 Extra test: value" in caplog.text
        assert caplog.records[0].custom == "custom_value"


def test_log_with_extra_none(debug, caplog):
    """Test that log method handles extra=None by setting it to empty dict.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.lv1("Test: %s", "value", extra=None)
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.lv1("Extra none test: %s", "value", extra=None)
        assert "DEBUG1 Extra none test: value" in caplog.text
        # No errors, logs successfully with extra={}


def test_log_all_parameters_combined(debug, caplog):
    """Test log method with exc_info, stack_info, and extra combined.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> try:
        ...     raise ValueError("Test")
        ... except ValueError:
        ...     debug.lv1("Test: %s", "value", exc_info=True, stack_info=True,
        ...               extra={"custom": "value"})
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        try:
            raise ValueError("Combined test error")
        except ValueError:
            debug.lv1(
                "Combined test: %s",
                "value",
                exc_info=True,
                stack_info=True,
                stacklevel=4,
                extra={"custom": "combined_value"},
            )
        assert "DEBUG1 Combined test: value" in caplog.text
        assert "ValueError: Combined test error" in caplog.text
        assert "Stack (most recent call last):" in caplog.text
        assert caplog.records[0].custom == "combined_value"


def test_log_with_invalid_extra_type(debug, caplog):
    """Test that log method handles invalid extra type gracefully.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.lv1("Test: %s", "value", extra="invalid")  # Raises TypeError
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )
    expected = "Invalid extra test"
    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        with pytest.raises(TypeError):
            debug.lv1(
                "Invalid extra test: %s",
                "value",
                extra="not_a_dict",
            )
            assert expected not in caplog.text


def test_log_with_empty_message(debug, caplog):
    """Test that log method handles empty message.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.lv1("")  # Should log empty message
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.lv1("")
        assert "DEBUG1 " in caplog.text  # Empty message logged


def test_log_with_multiple_handlers(debug, caplog):
    """Test that log method works with multiple handlers.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler1 = logging.StreamHandler()
        >>> handler2 = logging.StreamHandler()
        >>> debug.add_handler(handler1)
        >>> debug.add_handler(handler2)
        >>> debug.lv1("Test: %s", "value")
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    handler1 = logging.StreamHandler()
    handler2 = logging.StreamHandler()
    formatter = logging.Formatter("%(funcName)s:%(lineno)d %(message)s")
    before = len(debug.logger.handlers)
    debug.add_handler(handler1, formatter=formatter)
    debug.add_handler(handler2, formatter=formatter)

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.lv1("Multi-handler test: %s", "value")
        assert "DEBUG1 Multi-handler test: value" in caplog.text
        assert len(debug.logger.handlers) == before + 2  # Two handlers added


def test_log_performance(debug, caplog):
    """Test that log method performs efficiently with new parameters.

    Args:
        debug: TieredDebug instance. (TieredDebug)
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> debug = TieredDebug(level=1)
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> for _ in range(10):
        ...     debug.lv1("Test: %s", "value")
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 1
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        for _ in range(100):  # Test 100 log calls
            debug.lv1(
                "Performance test: %s",
                str(_),
                extra={"count": _},
            )
        assert "DEBUG1 Performance test:" in caplog.text
        assert len(caplog.records) == 100  # All calls logged
