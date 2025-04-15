"""Unit tests for the base module."""

# pylint: disable=W0212
import logging
import importlib
import pytest
from tiered_debug import set_level, set_stacklevel, lv1, lv2, lv3, lv4, lv5
import tiered_debug._base as base

ENVVAR = "TIERED_DEBUG_LEVEL"


# Fixture to reset global state before each test
@pytest.fixture(autouse=True)
def reset_state():
    """
    Reset the global _level and _stacklevel to their default values before each test.
    """
    base._level = 1
    base._stacklevel = 2


# Tests for set_level
def test_set_level_valid():
    """Test that set_level sets _level correctly for valid inputs."""
    set_level(1)
    assert base._level == 1
    set_level(3)
    assert base._level == 3
    set_level(5)
    assert base._level == 5


def test_set_level_invalid():
    """Test that set_level raises ValueError for invalid inputs."""
    with pytest.raises(ValueError, match="Debug level must be between 1 and 5"):
        set_level(0)
    with pytest.raises(ValueError, match="Debug level must be between 1 and 5"):
        set_level(6)


def test_set_level_with_override(monkeypatch):
    """Test that set_level with override=True overrides the environment variable."""
    # Set environment variable
    monkeypatch.setenv(ENVVAR, "4")
    importlib.reload(base)
    assert base._level == 4  # Confirm env var was applied

    # Override with set_level
    set_level(2, override=True)
    assert base._level == 2  # Should override environment variable

    # Test with invalid level
    with pytest.raises(ValueError, match="Debug level must be between 1 and 5"):
        set_level(6, override=True)


def test_set_level_without_override(monkeypatch):
    """Test that set_level with override=False doesn't override the environment variable."""
    # Set environment variable
    monkeypatch.setenv(ENVVAR, "5")
    importlib.reload(base)
    assert base._level == 5  # Confirm env var was applied

    # Try to change without override
    set_level(2, override=False)
    assert base._level == 5  # Should not change because env var is set

    # Try with explicit override=False
    set_level(3, override=False)
    assert base._level == 5  # Should still not change

    # Check with invalid level (shouldn't even validate since no change happens)
    set_level(7, override=False)
    assert base._level == 5  # Should remain unchanged


def test_set_level_no_env_var(monkeypatch):
    """Test that set_level works when no environment variable is set."""
    # Clear any environment variable
    monkeypatch.delenv(ENVVAR, raising=False)
    importlib.reload(base)

    # Try to set level without override when no env var exists
    set_level(3)
    assert base._level == 3  # Should change because no env var

    # Try with explicit override=False
    set_level(4, override=False)
    assert base._level == 4  # Should still change


# Tests for set_stacklevel
def test_set_stacklevel_valid():
    """Test that set_stacklevel sets _stacklevel correctly for valid inputs."""
    set_stacklevel(1)
    assert base._stacklevel == 1
    set_stacklevel(2)
    assert base._stacklevel == 2
    set_stacklevel(3)
    assert base._stacklevel == 3


def test_set_stacklevel_invalid():
    """Test that set_stacklevel raises ValueError for invalid inputs."""
    with pytest.raises(ValueError, match="stacklevel must be between 1 and 9"):
        set_stacklevel(0)
    with pytest.raises(ValueError, match="stacklevel must be between 1 and 9"):
        set_stacklevel(10)


# Tests for initialization based on environment variable
def test_initial_level_from_env(monkeypatch):
    """Test that _level is set from a valid environment variable."""
    monkeypatch.setenv(ENVVAR, "4")
    importlib.reload(base)
    assert base._level == 4


def test_initial_level_invalid_env(monkeypatch):
    """Test that _level defaults to 1 with an invalid environment variable."""
    monkeypatch.setenv(ENVVAR, "invalid")
    importlib.reload(base)
    assert base._level == 1


def test_initial_level_out_of_range_env(monkeypatch):
    """Test that _level defaults to 1 when environment variable is out of range."""
    monkeypatch.setenv(ENVVAR, "6")
    importlib.reload(base)
    assert base._level == 1
    monkeypatch.setenv(ENVVAR, "0")
    importlib.reload(base)
    assert base._level == 1


def test_initial_level_not_set(monkeypatch):
    """Test that _level defaults to 1 when environment variable is not set."""
    monkeypatch.delenv(ENVVAR, raising=False)
    importlib.reload(base)
    assert base._level == 1


# Tests for logging functions using parametrize
@pytest.mark.parametrize(
    "level, should_log",
    [
        (1, True),
        (2, True),
        (3, True),
        (4, True),
        (5, True),
    ],
)
def test_lv1_logs(caplog, level, should_log):
    """Test that lv1 logs messages when _level >= 1."""
    set_level(level)
    with caplog.at_level(logging.DEBUG):
        lv1("Test message")
    assert ("DEBUG1 Test message" in caplog.text) == should_log


@pytest.mark.parametrize(
    "level, should_log",
    [
        (1, False),
        (2, True),
        (3, True),
        (4, True),
        (5, True),
    ],
)
def test_lv2_logs(caplog, level, should_log):
    """Test that lv2 logs messages when _level >= 2."""
    set_level(level)
    with caplog.at_level(logging.DEBUG):
        lv2("Test message")
    assert ("DEBUG2 Test message" in caplog.text) == should_log


@pytest.mark.parametrize(
    "level, should_log",
    [
        (1, False),
        (2, False),
        (3, True),
        (4, True),
        (5, True),
    ],
)
def test_lv3_logs(caplog, level, should_log):
    """Test that lv3 logs messages when _level >= 3."""
    set_level(level)
    with caplog.at_level(logging.DEBUG):
        lv3("Test message")
    assert ("DEBUG3 Test message" in caplog.text) == should_log


@pytest.mark.parametrize(
    "level, should_log",
    [
        (1, False),
        (2, False),
        (3, False),
        (4, True),
        (5, True),
    ],
)
def test_lv4_logs(caplog, level, should_log):
    """Test that lv4 logs messages when _level >= 4."""
    set_level(level)
    with caplog.at_level(logging.DEBUG):
        lv4("Test message")
    assert ("DEBUG4 Test message" in caplog.text) == should_log


@pytest.mark.parametrize(
    "level, should_log",
    [
        (1, False),
        (2, False),
        (3, False),
        (4, False),
        (5, True),
    ],
)
def test_lv5_logs(caplog, level, should_log):
    """Test that lv5 logs messages when _level >= 5."""
    set_level(level)
    with caplog.at_level(logging.DEBUG):
        lv5("Test message")
    assert ("DEBUG5 Test message" in caplog.text) == should_log


# Tests for fmap function
def test_fmap_returns_correct_mapping():
    """Test that fmap returns a dictionary with the correct keys and functions."""
    mapping = base.FMAP

    # Check that the mapping has the expected keys
    assert set(mapping.keys()) == {1, 2, 3, 4, 5}

    # Check that the values are the correct functions
    assert mapping[1].__name__ == lv1.__name__
    assert mapping[2].__name__ == lv2.__name__
    assert mapping[3].__name__ == lv3.__name__
    assert mapping[4].__name__ == lv4.__name__
    assert mapping[5].__name__ == lv5.__name__


# Tests for begin_end decorator
def test_begin_end_decorator(caplog):
    """Test that the begin_end decorator logs function entry and exit."""
    set_level(3)  # Set level high enough to capture both logs

    # Create a decorated function
    @base.begin_end(begin=2, end=3)
    def test_function():
        return "test result"

    # Call the function and capture logs
    with caplog.at_level(logging.DEBUG):
        result = test_function()

    # Check the result and logs
    assert result == "test result"
    assert "DEBUG2 BEGIN CALL: test_function()" in caplog.text
    assert "DEBUG3 END CALL: test_function()" in caplog.text


def test_begin_end_with_custom_levels(caplog):
    """Test that the begin_end decorator works with custom levels."""
    set_level(5)  # Set level high enough to capture both logs

    # Create a decorated function with custom levels
    @base.begin_end(begin=4, end=5)
    def test_function():
        return "test result"

    # Call the function and capture logs
    with caplog.at_level(logging.DEBUG):
        result = test_function()

    # Check the result and logs
    assert result == "test result"
    assert "DEBUG4 BEGIN CALL: test_function()" in caplog.text
    assert "DEBUG5 END CALL: test_function()" in caplog.text


def test_begin_end_respects_debug_level(caplog):
    """Test that the begin_end decorator respects the current debug level."""
    set_level(3)  # Set level to only show begin message but not end

    # Create a decorated function with levels that should be partially filtered
    @base.begin_end(begin=3, end=4)
    def test_function():
        return "test result"

    # Call the function and capture logs
    with caplog.at_level(logging.DEBUG):
        result = test_function()

    # Check the result and logs
    assert result == "test result"
    assert "DEBUG3 BEGIN CALL: test_function()" in caplog.text
    assert "DEBUG4 END CALL: test_function()" not in caplog.text


# Tests for custom stacklevel and stack index parameters
def test_custom_stacklevel_parameter(caplog):
    """Test that the stklvl parameter affects the stacklevel used."""
    set_level(5)

    # Create a function that uses a custom stacklevel
    def inner_function():
        lv1("Custom stacklevel test", stklvl=1)

    # Call and verify
    with caplog.at_level(logging.DEBUG):
        inner_function()

    assert "Custom stacklevel test" in caplog.text
    # The logger name will be different with stacklevel=1 vs the default of 2
    # We're primarily testing that the parameter is accepted and used


# Tests for lv1's unconditional logging (no level check)
def test_lv1_logs_unconditionally(caplog):
    """Test that lv1 logs messages without checking debug level."""
    # Store original level
    original_level = base._level

    try:
        # Temporarily set _level to a value that would block other log levels
        # We have to use a valid value since there are checks in set_level
        set_level(1)

        # Clear log
        caplog.clear()

        # lv1 should log regardless of level
        with caplog.at_level(logging.DEBUG):
            lv1("Unconditional message")
            lv2("Conditional message")  # Should not log

        # Verify lv1 logged but lv2 didn't
        assert "DEBUG1 Unconditional message" in caplog.text
        assert "DEBUG2 Conditional message" not in caplog.text
    finally:
        # Restore original level
        base._level = original_level


# Test for logger name setting in lv1
def test_lv1_sets_logger_name(caplog):
    """Test that lv1 sets the logger name correctly using _get_logger_name."""
    with caplog.at_level(logging.DEBUG):
        lv1("Logger name test")

    # Verify the logger name is set correctly (should be this module's name)
    assert caplog.records[0].name == __name__
