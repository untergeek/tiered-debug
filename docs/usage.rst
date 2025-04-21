.. _usage:

Usage
=====

The ``tiered-debug`` module provides flexible debug logging for Python projects.
This guide shows how to use the ``TieredDebug`` class directly or via the
``debug.py`` module for project-wide debugging with customizable log levels and
metadata.

Using TieredDebug Directly
--------------------------

Create a ``TieredDebug`` instance and add handlers as needed:

.. code-block:: python

   from tiered_debug import TieredDebug
   import logging

   debug = TieredDebug(level=3)
   debug.add_handler(
       logging.StreamHandler(),
       formatter=logging.Formatter(
           "%(asctime)s %(funcName)s:%(lineno)d %(context)s %(message)s"
       )
   )

   debug.lv1("Level 1: %s", "always logs")  # Always logs
   debug.lv3("Level 3: %s", "logs", extra={"context": "test"})  # Logs (level <= 3)
   debug.lv5("Level 5 message")  # Ignored (level > 3)

Use the ``change_level`` context manager for temporary level changes:

.. code-block:: python

   with debug.change_level(5):
       debug.lv5("Temporary high-level log")  # Logs
   debug.lv5("Ignored again")  # Ignored

Using ``debug.py`` for Project-Wide Debugging
---------------------------------------------

Copy the contents of :doc:`debug.py <debug>` into your project to use a global
``TieredDebug`` instance:

1. **Configure the logger** in ``debug.py``:

   .. code-block:: python

      # debug.py
      from tiered_debug.debug import debug
      import logging

      debug.add_handler(
          logging.StreamHandler(),
          formatter=logging.Formatter(
              "%(asctime)s %(levelname)-9s %(name)22s "
              "%(funcName)22s:%(lineno)-4d %(module)s %(message)s"
          )
      )

2. **Use in other modules**:

   .. code-block:: python

      # my_module.py
      from .debug import debug, begin_end

      @begin_end(begin=2, end=3, stacklevel=2, extra={"module": "my_module"})
      def process_task(task_id: str):
          debug.lv1(f"Task %s started", task_id)

      process_task("123")  # Logs BEGIN at 2, message at 1, END at 3

Regarding the ``begin_end`` decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The decorator wraps functions to log entry and exit at specified debug levels:

.. code-block:: python

   from .debug import debug, begin_end

   debug.level = 3

   @begin_end(begin=2, end=3, extra={"module": "my_module"})
   def my_function():
       debug.lv1("My function executed")

   def run():
       my_function()

This produces log output like:

.. code-block:: bash

   2025-05-20 10:00:00,000 DEBUG       my_module           run:12   my_module DEBUG2 BEGIN CALL: my_function()
   2025-05-20 10:00:00,001 DEBUG       my_module   my_function:8    my_module DEBUG1 My function executed
   2025-05-20 10:00:00,002 DEBUG       my_module           run:12   my_module DEBUG3 END CALL: my_function()

The ``BEGIN`` and ``END`` messages appear at the call site (``run:12``) due to
the decorator’s wrapping logic, which logs at the point of function invocation.

Elasticsearch Logging
--------------------

Add an Elasticsearch handler to log to an index (requires ``elasticsearch``):

.. code-block:: python

   from logging.handlers import BufferingHandler
   from elasticsearch import Elasticsearch

   class ESHandler(BufferingHandler):
       def __init__(self, es_host: str, index: str):
           super().__init__(capacity=1000)
           self.es = Elasticsearch([es_host])
           self.index = index

       def flush(self):
           for record in self.buffer:
               body = {
                   "message": record.getMessage(),
                   "level": record.levelname,
                   "context": getattr(record, "context", None)
               }
               self.es.index(index=self.index, body=body)
           self.buffer.clear()

   debug = TieredDebug()
   debug.add_handler(
       ESHandler("localhost:9200", "debug-logs"),
       formatter=logging.Formatter("%(context)s %(message)s")
   )
   debug.lv1("Logged to ES", extra={"context": "test"})

Testing with pytest
-------------------

Use pytest’s ``caplog`` fixture to test logging:

.. code-block:: python

   from tiered_debug import TieredDebug
   import logging

   def test_logging(caplog):
       debug = TieredDebug(level=2)
       debug.add_handler(
           logging.StreamHandler(),
           formatter=logging.Formatter(
               "%(funcName)s:%(lineno)d %(context)s %(message)s"
           )
       )
       with caplog.at_level(logging.DEBUG, logger=debug.logger.name):
           debug.lv2("Test: %s", "value", extra={"context": "test"})
           assert "DEBUG2 Test: value" in caplog.text
           assert caplog.records[0].context == "test"
