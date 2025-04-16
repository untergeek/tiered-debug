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
    - [Best Practices](#best-practices)
    - [Advanced](#advanced)
    - [Decorator](#decorator)
    - [Configuring the global `stacklevel`](#configuring-the-global-stacklevel)
  - [License](#license)

## Description

The class in this module provides a way to enable multiple tiers of debug logging.
It's not doing anything fancy. It's just a wrapper around a standard `logger.debug()`
call that caps the highest tier of debug logging to a value which can be set at
class instantiation, or defaults to 1. It's a class attribute, `.level`, which can
be set to any value between 1 and 5 at any time.

## Installation

```console
pip install -U tiered-debug
```

## Usage

### Basic

```python
from tiered_debug import TieredDebug

# Establish a class instance
debug = TieredDebug()

# Set the debug level for this class instance
debug.set_level(3)

# Log messages from any module
debug.lv1("This will log")  # Logs because 1 <= 3
debug.lv3("This will log")  # Logs because 3 <= 3
debug.lv4("This won't log") # Doesn't log because 4 > 3
```

### Best Practices

Make use of the sample [`debug.py`](src/tiered_debug/debug.py) module. Deploy it
in your own project at the root level as-is and it should be usable:

```python
from .debug import debug

debug.lv1("This will now log")
```

You can also use the `@begin_end()` decorator factory function to put `BEGIN` and
`END` debug messages before and after the function or method runs:

```python
from .debug import debug, begin_end

@begin_end()
def my_function():
    debug.lv1("This is in the function")

def other_function():
    my_function()
```

### Advanced

Each "level" can manually override default settings using these keyword arguments:

```python
def lv[1-5](self, msg: str, stklvl: t.Optional[StackLevel] = None) -> None:
```

These will simply default to `self.stacklevel` if no value for `stklvl` is given.

The ability to manually override the `stacklevel`, stack index number, and frame
index number are in case you ever need to reference something that isn't caught
by `@wraps` correctly, or make a custom decorator, or similar.

### Decorator

The decorator can be applied like any other, but there's an interesting side effect
to wrapping logging statements before and after a function or method:

```python
from .debug import debug, begin_end

debug.set_level(3)


@begin_end()
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

### Configuring the global `stacklevel`

The `stacklevel` parameter is passed to the `logging.debug()` function as the
`stacklevel` argument. The `stacklevel` parameter is the stack level to use for
the log message. The default value is `2`, which means that the log message will
appear to come from the caller of the caller each `lv#` method. In other words,
if you call `lv1()` from a function, the log message will appear to come from that
function rather than from `lv1()` or the `TieredDebug` class. If your log formatter
is set up to include the module name, function name, and/or line of code in the log
message, having the stacklevel properly set will ensure the correct data is
displayed.

In the event that you use this module as part of another module or class, you may
need to increase the `stacklevel` to 3. This can be done using the
`.stacklevel` attribute. This will need to be done before any logging takes
place.

## License

`tiered-debug` is distributed under the terms of the [Apache](LICENSE) license.

©Copyright 2025 Aaron Mildenstein
