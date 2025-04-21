"""Unit tests for the tiered_debug.debug module.

Tests the global `debug` instance and `begin_end` decorator in `debug.py`,
which provide project-wide debugging for tiered logging at levels 1-5.
Tests cover initialization, decorator behavior, and logging integration,
designed for projects like ElasticKeeper and ElasticCheckpoint.

Examples:
    >>> from tiered_debug.debug import debug, begin_end
    >>> import logging
    >>> debug.level = 3
    >>> debug.add_handler(logging.StreamHandler(), logging.Formatter(
    ...     "%(funcName)s:%(lineno)d %(message)s"))
    >>> @begin_end(debug, begin=2, end=3, extra={"func": "test"})
    ... def test_func():
    ...     debug.lv1("Inside")
    >>> test_func()  # Logs BEGIN at 2, Inside at 1, END at 3
"""

# pylint: disable=W0107,W0212,W0621
import logging
import pytest
from tiered_debug import TieredDebug
from tiered_debug.debug import begin_end, DEFAULT_BEGIN, DEFAULT_END
from tiered_debug.debug import debug as sample_debug

BASENAME = "tiered_debug.debug"
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
    sample_debug._logger.name = __name__
    return sample_debug


@pytest.fixture
def reset_debug(monkeypatch):
    """Reset the global debug instance for each test.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        TieredDebug: Fresh TieredDebug instance as global debug.

    Examples:
        >>> from tiered_debug import debug
        >>> isinstance(debug, TieredDebug)
        True
    """
    new_debug = TieredDebug()
    monkeypatch.setattr("tiered_debug.debug.debug", new_debug)
    return new_debug


# Tests for global debug instance
def test_debug_instance(debug):
    """Test that global debug is a TieredDebug instance with defaults.

    Args:
        debug: Global TieredDebug instance.

    Examples:
        >>> from tiered_debug import debug
        >>> isinstance(debug, TieredDebug)
        True
    """
    assert isinstance(debug, TieredDebug)
    assert debug.level == 1  # Default debug level
    assert debug.stacklevel == 3  # Default stack level
    assert debug.logger.name == __name__


def test_debug_add_handler(debug, caplog):
    """Test that global debug supports handler configuration.

    Args:
        debug: Global TieredDebug instance.
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> from tiered_debug import debug
        >>> import logging
        >>> handler = logging.StreamHandler()
        >>> debug.add_handler(handler)
        >>> debug.lv1("Test")
    """
    caplog.set_level(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(funcName)s:%(lineno)d %(message)s")
    debug.add_handler(handler, formatter=formatter)

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        debug.lv1("Test message")
        assert "DEBUG1 Test message" in caplog.text
        assert handler in debug.logger.handlers


# Tests for constants
def test_default_begin():
    """Test that DEFAULT_BEGIN is correctly set.

    Examples:
        >>> from tiered_debug.debug import DEFAULT_BEGIN
        >>> DEFAULT_BEGIN
        2
    """
    assert DEFAULT_BEGIN == 2
    assert isinstance(DEFAULT_BEGIN, int)


def test_default_end():
    """Test that DEFAULT_END is correctly set.

    Examples:
        >>> from tiered_debug.debug import DEFAULT_END
        >>> DEFAULT_END
        3
    """
    assert DEFAULT_END == 3
    assert isinstance(DEFAULT_END, int)


# Tests for begin_end decorator
def test_begin_end_default_levels(debug, caplog):
    """Test that begin_end logs BEGIN and END at default levels.

    Args:
        debug: Global TieredDebug instance.
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> from tiered_debug.debug import begin_end
        >>> import logging
        >>> debug = TieredDebug(level=3)
        >>> debug.add_handler(logging.StreamHandler())
        >>> @begin_end()
        ... def test_func():
        ...     debug.lv1("Inside")
        >>> test_func()
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 3
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    @begin_end()
    def test_func():
        debug.lv1("Inside")

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        test_func()
        assert "DEBUG2 BEGIN CALL: test_func()" in caplog.text
        assert "DEBUG1 Inside" in caplog.text
        assert "DEBUG3 END CALL: test_func()" in caplog.text


@pytest.mark.parametrize(
    "begin,end,should_log_begin,should_log_end",
    [
        (1, 1, True, True),  # Both log at level 1
        (2, 3, True, False),  # Begin logs, end doesn't (level=2)
        (3, 2, False, True),  # End logs, begin doesn't (level=2)
        (4, 4, False, False),  # Neither logs (level=2)
    ],
)
def test_begin_end_custom_levels(
    debug, caplog, begin, end, should_log_begin, should_log_end
):
    """Test that begin_end respects custom begin and end levels.

    Args:
        debug: Global TieredDebug instance.
        caplog: Pytest caplog fixture for capturing logs.
        begin: Debug level for BEGIN message. (int)
        end: Debug level for END message. (int)
        should_log_begin: Whether BEGIN should be logged. (bool)
        should_log_end: Whether END should be logged. (bool)

    Examples:
        >>> from tiered_debug.debug import begin_end
        >>> import logging
        >>> debug = TieredDebug(level=2)
        >>> debug.add_handler(logging.StreamHandler())
        >>> @begin_end(begin=1, end=2)
        ... def test_func():
        ...     pass
        >>> test_func()
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 2
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    @begin_end(begin=begin, end=end)
    def test_func():
        pass

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        test_func()
        begin_msg = f"DEBUG{begin} BEGIN CALL: test_func()"
        end_msg = f"DEBUG{end} END CALL: test_func()"
        assert (begin_msg in caplog.text) == should_log_begin
        assert (end_msg in caplog.text) == should_log_end


def test_begin_end_invalid_levels(debug, caplog):
    """Test that begin_end handles invalid begin/end levels with defaults.

    Args:
        debug: Global TieredDebug instance.
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> from tiered_debug.debug import begin_end
        >>> import logging
        >>> debug = TieredDebug(level=3)
        >>> debug.add_handler(logging.StreamHandler())
        >>> @begin_end(begin=6, end=7)
        ... def test_func():
        ...     pass
        >>> test_func()
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 3
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    @begin_end(begin=6, end=7)
    def test_func():
        pass

    with caplog.at_level(logging.DEBUG):
        with pytest.raises(ValueError):
            test_func()
        assert len(caplog.text) == 0


def test_begin_end_custom_debug_instance(caplog):
    """Test that begin_end works with a custom TieredDebug instance.

    Args:
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> from tiered_debug.debug import begin_end
        >>> import logging
        >>> debug = TieredDebug(level=3)
        >>> debug.add_handler(logging.StreamHandler())
        >>> @begin_end(debug, begin=2, end=3)
        ... def test_func():
        ...     debug.lv1("Inside")
        >>> test_func()
    """
    caplog.set_level(logging.DEBUG)
    custom_debug = TieredDebug(level=3)
    custom_debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    @begin_end(debug_obj=custom_debug, begin=2, end=3)
    def test_func():
        custom_debug.lv1("Inside")

    with caplog.at_level(logging.DEBUG, logger=custom_debug.logger.name):
        test_func()
        assert "DEBUG2 BEGIN CALL: test_func()" in caplog.text
        assert "DEBUG1 Inside" in caplog.text
        assert "DEBUG3 END CALL: test_func()" in caplog.text
        assert len(caplog.records) == 3


def test_begin_end_custom_stacklevel(debug, caplog):
    """Test that begin_end uses custom stacklevel correctly.

    Args:
        debug: Global TieredDebug instance.
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> from tiered_debug.debug import begin_end
        >>> import logging
        >>> debug = TieredDebug(level=3)
        >>> debug.add_handler(logging.StreamHandler())
        >>> @begin_end(begin=2, end=3, stacklevel=4)
        ... def test_func():
        ...     pass
        >>> test_func()
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 3
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )
    expected = "_pytest.python"

    @begin_end(begin=2, end=3, stacklevel=3)
    def test_func():
        pass

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        test_func()
        assert caplog.records[0].name == expected


def test_begin_end_with_extra(debug, caplog):
    """Test that begin_end passes extra metadata correctly.

    Args:
        debug: Global TieredDebug instance.
        caplog: Pytest caplog fixture for capturing logs.

    Examples:
        >>> from tiered_debug.debug import begin_end
        >>> import logging
        >>> debug = TieredDebug(level=3)
        >>> debug.add_handler(logging.StreamHandler())
        >>> @begin_end(begin=2, end=3, extra={"func": "test"})
        ... def test_func():
        ...     pass
        >>> test_func()
    """
    caplog.set_level(logging.DEBUG)
    debug.level = 3
    debug.add_handler(
        logging.StreamHandler(),
        formatter=logging.Formatter("%(funcName)s:%(lineno)d %(message)s"),
    )

    @begin_end(begin=2, end=3, extra={"func": "test"})
    def test_func():
        pass

    with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
        test_func()
        assert "DEBUG2 BEGIN CALL: test_func()" in caplog.text
        assert "DEBUG3 END CALL: test_func()" in caplog.text
        assert caplog.records[0].func == "test"
        assert caplog.records[1].func == "test"


def test_begin_end_preserves_function_metadata():
    """Test that begin_end preserves function metadata via functools.wraps.

    Examples:
        >>> from tiered_debug.debug import begin_end
        >>> def test_func():
        ...     '''Test docstring.'''
        ...     pass
        >>> decorated = begin_end()(test_func)
        >>> decorated.__name__
        'test_func'
    """

    def test_func():
        """Test function docstring."""
        pass

    decorated = begin_end()(test_func)
    assert decorated.__name__ == "test_func"
    assert decorated.__doc__ == "Test function docstring."
