"""Unit tests for the tiered_debug._base module."""

# pylint: disable=W0212,W0603
import logging
import pytest
from tiered_debug._base import DEFAULTS, TieredDebug, logger

# Create a global instance for testing
debug = TieredDebug()


# Fixture to reset the debug instance before each test
@pytest.fixture(autouse=True)
def reset_state():
    """
    Reset the debug instance to its default values before each test.
    Also clear any environment variables that might affect tests.
    """
    global debug
    debug = TieredDebug()
    # Reset the logger name in case it was changed by tests
    logger.name = __name__


# Tests for level property and setter
def test_level_property():
    """Test that level property returns the current level."""
    debug._level = 3
    assert debug.level == 3


def test_level_setter_valid():
    """Test that level setter sets level correctly for valid inputs."""
    debug.level = 1
    assert debug._level == 1
    debug.level = 3
    assert debug._level == 3
    debug.level = 5
    assert debug._level == 5


def test_level_setter_invalid(caplog):
    """Test that level setter handles invalid inputs correctly."""
    with caplog.at_level(logging.WARNING):
        debug.level = 0
        assert "Invalid debug level" in caplog.text
        assert debug.level == 1  # Default value

    caplog.clear()

    with caplog.at_level(logging.WARNING):
        debug.level = 6
        assert "Invalid debug level" in caplog.text
        assert debug.level == 1  # Default value


# Tests for stacklevel property and setter
def test_stacklevel_property():
    """Test that stacklevel property returns the current stacklevel."""
    debug._stacklevel = 3
    assert debug.stacklevel == 3


def test_stacklevel_setter_valid():
    """Test that stacklevel setter sets stacklevel correctly for valid inputs."""
    debug.stacklevel = 1
    assert debug._stacklevel == 1
    debug.stacklevel = 3
    assert debug._stacklevel == 3
    debug.stacklevel = 9
    assert debug._stacklevel == 9


def test_stacklevel_setter_invalid(caplog):
    """Test that stacklevel setter handles invalid inputs correctly."""
    with caplog.at_level(logging.WARNING):
        debug.stacklevel = 0
        assert "Invalid stack level" in caplog.text
        assert debug.stacklevel == DEFAULTS["stack"]  # Default value

    caplog.clear()

    with caplog.at_level(logging.WARNING):
        debug.stacklevel = 10
        assert "Invalid stack level" in caplog.text
        assert debug.stacklevel == DEFAULTS["stack"]  # Default value


# Tests for check_val method
def test_check_val_valid():
    """Test that check_val returns valid values unchanged."""
    assert debug.check_val(3, "debug") == 3
    assert debug.check_val(5, "debug") == 5
    assert debug.check_val(3, "stack") == 3
    assert debug.check_val(9, "stack") == 9


def test_check_val_invalid(caplog):
    """Test that check_val returns default values for invalid inputs."""
    with caplog.at_level(logging.WARNING):
        assert debug.check_val(0, "debug") == DEFAULTS["debug"]
        assert "Invalid debug level" in caplog.text

    caplog.clear()

    with caplog.at_level(logging.WARNING):
        assert debug.check_val(10, "stack") == DEFAULTS["stack"]
        assert "Invalid stack level" in caplog.text


# Tests for _get_logger_name method
def test_get_logger_name_valid():
    """Test that _get_logger_name returns correct module name."""
    # For a valid stack level, it should return the module name
    # In the code this does return sys._getframe(level).f_globals["__name__"]
    # removing one from `level` to get the correct frame. So to get the current
    # module name, we need to pass 1 here to get the caller's frame.
    name = debug._get_logger_name(1)
    assert name == __name__


def test_get_logger_name_invalid():
    """Test that _get_logger_name handles invalid inputs."""
    # For an invalid stack level, it should return "unknown"
    name = debug._get_logger_name(100)  # Too deep
    assert name == "unknown"


# Tests for change_level context manager
def test_change_level():
    """Test that change_level temporarily changes the level."""
    debug.level = 2
    assert debug.level == 2

    with debug.change_level(4):
        assert debug.level == 4

    # After context, level should be restored
    assert debug.level == 2


def test_change_level_with_exception():
    """Test that change_level restores level even if exception occurs."""
    debug.level = 2

    try:
        with debug.change_level(4):
            assert debug.level == 4
            raise RuntimeError("Test exception")
    except RuntimeError:
        pass

    # Level should be restored despite exception
    assert debug.level == 2


# Tests for log method
def test_log_with_default_stacklevel():
    """Test that log uses the default stacklevel if none provided."""
    debug.stacklevel = DEFAULTS["stack"]
    # Spy on _get_logger_name to check what stacklevel is passed
    original_get_logger_name = debug._get_logger_name
    called_with = None

    def mock_get_logger_name(level):
        nonlocal called_with
        called_with = level
        return original_get_logger_name(level)

    debug._get_logger_name = mock_get_logger_name

    try:
        debug.log(1, "test", None)
        assert called_with == DEFAULTS["stack"]  # Should use default stacklevel
    finally:
        debug._get_logger_name = original_get_logger_name


def test_log_with_custom_stacklevel():
    """Test that log uses the provided stacklevel."""
    debug.stacklevel = 3
    # Spy on _get_logger_name to check what stacklevel is passed
    original_get_logger_name = debug._get_logger_name
    called_with = None

    def mock_get_logger_name(level):
        nonlocal called_with
        called_with = level
        return original_get_logger_name(level)

    debug._get_logger_name = mock_get_logger_name

    try:
        debug.log(1, "test", 4)
        assert called_with == 4  # Should use provided stacklevel
    finally:
        debug._get_logger_name = original_get_logger_name


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
def test_log_levels(caplog, debug_level, log_level, should_log):
    """Test that log functions respect the current debug level."""
    debug.level = debug_level

    # Map log_level to the corresponding method
    log_methods = {
        1: debug.lv1,
        2: debug.lv2,
        3: debug.lv3,
        4: debug.lv4,
        5: debug.lv5,
    }

    # Clear log before test
    caplog.clear()

    # Call the appropriate log method
    with caplog.at_level(logging.DEBUG):
        log_methods[log_level](f"Test message level {log_level}")
    if should_log:
        assert caplog.records[0].name == __name__

    # Check if the message was logged
    expected = f"DEBUG{log_level} Test message level {log_level}"
    assert (expected in caplog.text) == should_log


# Test for lv1's unconditional logging
def test_lv1_logs_unconditionally(caplog):
    """Test that lv1 logs messages without checking debug level."""
    # Set level to minimum
    debug.level = 1

    # Clear log
    caplog.clear()

    # lv1 should log regardless of level
    with caplog.at_level(logging.DEBUG):
        debug.lv1("Unconditional message")
        debug.lv2("Conditional message")  # Should not log

    # Verify lv1 logged but lv2 didn't
    assert "DEBUG1 Unconditional message" in caplog.text
    assert "DEBUG2 Conditional message" not in caplog.text


# Tests for initialization
def test_default_initialization():
    """Test default initialization values."""
    instance = TieredDebug()
    assert instance.level == DEFAULTS["debug"]
    assert instance.stacklevel == DEFAULTS["stack"]


def test_custom_initialization():
    """Test initialization with custom values."""
    instance = TieredDebug(level=3, stacklevel=4)
    assert instance.level == 3
    assert instance.stacklevel == 4
