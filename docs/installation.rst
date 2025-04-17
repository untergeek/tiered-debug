.. _installation:

Installation
============

Requirements
------------

- Python 3.8 or higher

Install tiered-debug
--------------------

``tiered-debug`` is typically installed as a dependecy. 

1. **pyproject.toml**:

   Add ``tiered-debug`` to your ``pyproject.toml``:

   .. code-block:: toml

      dependencies = [
         'tiered-debug==1.2.0'
      ]

2. **setup.py**:

   If you are using ``setup.py``, add ``tiered-debug`` to your ``install_requires``:

   .. code-block:: python

      from setuptools import setup, find_packages

      setup(
          name='your_project',
          version='0.1.0',
          packages=find_packages(),
          install_requires=[
              'tiered-debug==1.2.0'
          ],
      )

3. **requirements.txt**:
   
   This is no longer common, but you can add ``tiered-debug`` to your ``requirements.txt``:


4. **Verify installation**:

   Test the module by running a simple script:

   .. code-block:: python

      from tiered_debug import TieredDebug
      debug = TieredDebug(level=2)
      debug.lv1("Test message")

Configuration
-------------

You can optionally configure the logger by adding a handler:

.. code-block:: python

   import logging
   debug = TieredDebug()
   debug.add_handler(logging.StreamHandler(), formatter=logging.Formatter(
       "%(asctime)s %(funcName)s:%(lineno)d %(message)s"))

For Elasticsearch logging, add a custom handler (see :ref:`usage`).
