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
    - [Configuring `stacklevel`](#configuring-stacklevel)
  - [License](#license)

## Description

This module provides a way to enable multiple tiers of debug logging. It's not
doing anything fancy. It's just a wrapper around a standard `logger.debug()`
call that caps the highest tier of debug logging to a value which can be set via
the environment variable `TIERED_DEBUG_LEVEL` at runtime, which has a default of 1,
but can be set to any value between 1 and 5. It can also be set interactively via
the `set_level()` function.


## Installation

```console
pip install tiered-debug
```

## Usage

```python
import tiered_debugging as debug

# Set the debug level globally (optional if using environment variable)
debug.set_level(3)

# Log messages from any module
debug.lv1("This will log")  # Logs because 1 <= 3
debug.lv3("This will log")  # Logs because 3 <= 3
debug.lv4("This won't log") # Doesn't log because 4 > 3
```

### Configuring `stacklevel`

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


## License

`tiered-debug` is distributed under the terms of the [Apache](LICENSE) license.

©Copyright 2025 Aaron Mildenstein
