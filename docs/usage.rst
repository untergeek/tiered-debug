.. _usage:

Usage
=====

The ``tiered-debug`` module provides flexible debug logging for Python projects.
This guide shows how to use the ``TieredDebug`` class directly or via the
``debug.py`` sample module for project-wide debugging.

Using TieredDebug Directly
--------------------------

Create a ``TieredDebug`` instance and optionally add additional handlers:

.. code-block:: python

   from tiered_debug import TieredDebug
   import logging

   debug = TieredDebug(level=3)
   # Optional: add a handler
   debug.add_handler(logging.StreamHandler(), formatter=logging.Formatter(
       "%(asctime)s %(funcName)s:%(lineno)d %(message)s"))

   debug.lv1("Level 1 message")  # Always logs
   debug.lv3("Level 3 message")  # Logs (level <= 3)
   debug.lv5("Level 5 message")  # Ignored (level > 3)

Use the ``change_level`` context manager for temporary level changes:

.. code-block:: python

   with debug.change_level(5):
       debug.lv5("Temporary high-level log")  # Logs
   debug.lv5("Ignored again")  # Ignored



Using ``debug.py`` for Project-Wide Debugging
---------------------------------------------

Copy the contents of :doc:`debug.py <debug>` into your project to use a global ``TieredDebug`` instance:

1. **Configure the logger** in ``debug.py``:

   .. code-block:: python

      # debug.py
      from debug import debug
      import logging

      debug.add_handler(logging.StreamHandler(), formatter=logging.Formatter(
          "%(asctime)s %(funcName)s:%(lineno)d %(message)s"))

2. **Use in other modules**:

   .. code-block:: python

      # my_module.py
      from .debug import debug, begin_end

      @begin_end(begin=2, end=3)
      def process_task(task_id: str):
          debug.lv1(f"Task {task_id} started")

      process_task("123")  # Logs BEGIN, message, END

Regarding the ``begin_end`` decorator:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The decorator can be applied like any other, but there's an interesting side effect
to wrapping logging statements before and after a function or method:

.. code-block:: python

   from .debug import debug, begin_end
   
   debug.set_level(3)
   
   
   @begin_end()
   def myfunction():
       debug.lv1("My function just executed")
   
   
   def run():
       myfunction()


With these values, the first and last log lines output from ``myfunction()`` will
look like this:

.. code-block:: bash

   2025-04-15 13:23:27,046 DEBUG       mymodule          run:12   DEBUG2 BEGIN CALL: myfunction()
   2025-04-15 13:23:27,046 DEBUG       mymodule   myfunction:8    DEBUG1 My function just executed
   2025-04-15 13:23:27,046 DEBUG       mymodule          run:12   DEBUG3 END CALL: myfunction()


Note that the ``BEGIN CALL`` log line appears to have been logged by the ``run()``
function, then the log from ``myfunction()``, then the ``END CALL`` line appears to
have been logged by the ``run()`` function again, and both ``CALL`` lines appear to
have come from the same line ``12``.  What's going on?

Well, the decorator is wrapping our function in between those two ``debug.lv#``
calls, and so Python has lovingly decided to make those appear right where the
call to ``myfunction()`` is made. It would be weird to *add* lines to the code,
wouldn't it? So here, the decorator is doing the logical thing, which is to make
it all happen right where the function is called.

Elasticsearch Logging
---------------------

Add an Elasticsearch handler for logging to an index (requires ``elasticsearch`` package):

.. code-block:: python

   from logging.handlers import BufferingHandler
   from elasticsearch import Elasticsearch

   class ElasticsearchHandler(BufferingHandler):
       def __init__(self, es_host: str, index_name: str):
           super().__init__(capacity=1000)
           self.es = Elasticsearch([es_host])
           self.index_name = index_name
       def flush(self):
           for record in self.buffer:
               self.es.index(
                   index=self.index_name,
                   body={"message": record.getMessage(), "level": record.levelname}
               )
           self.buffer.clear()

   debug = TieredDebug()
   debug.add_handler(ElasticsearchHandler("localhost:9200", "debug-logs"))
   debug.lv1("Logged to Elasticsearch")

Testing with pytest
-------------------

Use pytest's ``caplog`` fixture to test logging:

.. code-block:: python

   from tiered_debug import TieredDebug
   import logging

   def test_logging(caplog):
       debug = TieredDebug(level=2)
       debug.add_handler(logging.StreamHandler(), formatter=logging.Formatter(
           "%(funcName)s:%(lineno)d %(message)s"))
       with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
           debug.lv2("Test")
           assert "DEBUG2 Test" in caplog.text
