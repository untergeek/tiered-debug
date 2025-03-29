"""Unit tests for the base module."""

import logging
import importlib

# from os import environ
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
    with pytest.raises(ValueError, match="stacklevel must be between 1 and 3"):
        set_stacklevel(0)
    with pytest.raises(ValueError, match="stacklevel must be between 1 and 3"):
        set_stacklevel(4)


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
