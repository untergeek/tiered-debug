# tiered-debug

[![PyPI - Version](https://img.shields.io/pypi/v/tiered-debug.svg)](https://pypi.org/project/tiered-debug)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tiered-debug.svg)](https://pypi.org/project/tiered-debug)

-----

## Table of Contents

- [tiered-debug](#tiered-debug)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Basic](#basic)
    - [Advanced](#advanced)
    - [Decorator](#decorator)
    - [Configuring the global `stacklevel` and `stackindex`](#configuring-the-global-stacklevel-and-stackindex)
  - [License](#license)

## Description

This module provides a way to enable multiple tiers of debug logging. It's not
doing anything fancy. It's just a wrapper around a standard `logger.debug()`
call that caps the highest tier of debug logging to a value which can be set via
the environment variable `TIERED_DEBUG_LEVEL` at runtime, which has a default of 1,
but can be set to any value between 1 and 5. It can also be set interactively via
the `set_level()` function. A decorator generator called `begin_end` is also
included.

## Installation

```console
pip install tiered-debug
```

## Usage

### Basic

```python
import tiered_debugging as debug

# Set the debug level globally (optional if using environment variable)
debug.set_level(3)

# Log messages from any module
debug.lv1("This will log")  # Logs because 1 <= 3
debug.lv3("This will log")  # Logs because 3 <= 3
debug.lv4("This won't log") # Doesn't log because 4 > 3
```

### Advanced

Each "level" can manually override default settings using these keyword arguments:

```python
def lv[1-5](
    msg: str,
    stklvl: t.Optional[StackLevel] = _stacklevel,
    stkidx: t.Optional[int] = _stackindex,
    frmidx: t.Optional[int] = 0,
)
```

The default values are shown, with `_stacklevel` global to the module.

The ability to manually override the `stacklevel`, stack index number, and frame
index number are in case you ever need to reference something that isn't caught
by `@wraps` correctly, or make a custom decorator, or similar.

### Decorator

The provided `begin_end` decorator makes use of the `@wraps` decorator from
`functools` to ensure the proper stack information from the calling function is
passed to `func`. Note also that we are manually overriding the `stacklevel` for
our calls with `stklvl=_stacklevel + 1` and bumping our stack index value with
`stkidx=_stacklevel + 1`. These ensure that the lines being logged will include
the proper module and function names as well as the line number in the code.

The code looks like this:

```python
from functools import wraps

FMAP = {
    1: lv1,
    2: lv2,
    3: lv3,
    4: lv4,
    5: lv5,
}

def begin_end(begin: t.Optional[int] = 2, end: t.Optional[int] = 3) -> t.Callable:
    def decorator(func: t.Callable) -> t.Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            common = f"CALL: {func.__name__}()"
            FMAP[begin](f"BEGIN {common}", stklvl=_stacklevel + 1, stkidx=_stackindex + 1)
            result = func(*args, **kwargs)
            FMAP[end](f"END {common}", stklvl=_stacklevel + 1, stkidx=_stackindex + 1)
            return result
        return wrapper
    return decorator
```

The decorator can be applied like any other, but there's an interesting side effect
to wrapping logging statements before and after a function:

```python
import tiered_debug as debug

debug.set_level(3)


@debug.begin_end()
def myfunction():
    debug.lv1("My function just executed")


def run():
    myfunction()
```

With these values, the first and last log lines output from `myfunction()` will
look like this:

```text
2025-04-15 13:23:27,046 DEBUG       mymodule          run:12   DEBUG2 BEGIN CALL: myfunction()
2025-04-15 13:23:27,046 DEBUG       mymodule   myfunction:8    DEBUG1 My function just executed
2025-04-15 13:23:27,046 DEBUG       mymodule          run:12   DEBUG3 END CALL: myfunction()
```

Note that the `BEGIN CALL` log line appears to have been logged by the `run()`
function, then the log from `myfunction()`, then the `END CALL` line appears to
have been logged by the `run()` function again, and both `CALL` lines appear to
have come from the same line `12`.  What's going on?

Well, the decorator is wrapping our function in between those two `debug.lv#`
calls, and so Python has lovingly decided to make those appear right where the
call to `myfunction()` is made. It would be weird to *add* lines to the code,
wouldn't it? So here, the decorator is doing the logical thing, which is to make
it all happen right where the function is called.

### Configuring the global `stacklevel` and `stackindex`

The `stacklevel` parameter is passed to the `logging.debug()` function as the
`stacklevel` argument. The `stacklevel` parameter is the stack level to use for
the log message. The default value is 2, which means that the log message will
appear to come from the caller of the caller each `lv#` function. In other words,
if you call `lv1()` from a function, the log message will appear to come from the
caller of that function. If your log formatter is set up to include the module
name, function name, and/or line of code in the log message, having the stacklevel
properly set will ensure the correct data is displayed.

In the event that you use this module as part of another module or class, you may
need to increase the `stacklevel` to 3. This can be done using the
`set_stacklevel()` function. This will need to be done before any logging takes
place.

The same applies to the `stackindex` value, which is used to get the calling
module name. The default value is `1`, and can be set using the `set_stackindex()`
function.

## License

`tiered-debug` is distributed under the terms of the [Apache](LICENSE) license.

©Copyright 2025 Aaron Mildenstein
