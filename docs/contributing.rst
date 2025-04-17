.. _contributing:

Contributing
============

Contributions to ``tiered_debug`` are welcome! This guide outlines how to contribute to the project.

Getting Started
---------------

1. **Fork the repository** (if hosted on a platform like GitHub).
2. **Clone your fork**:

   .. code-block:: bash

      git clone https://github.com/your-username/tiered_debug.git
      cd tiered_debug

3. **Install dependencies**:

   .. code-block:: bash

      pip install pytest

4. **Run tests** to ensure the project is working:

   .. code-block:: bash

      pytest test_base.py -v

Submitting Changes
------------------

1. **Create a branch** for your changes:

   .. code-block:: bash

      git checkout -b my-feature

2. **Make changes** and commit with clear messages:

   .. code-block:: bash

      git commit -m "Add feature X to TieredDebug"

3. **Update tests** in ``test_base.py`` to cover your changes.
4. **Run tests** to verify:

   .. code-block:: bash

      pytest

5. **Push to your fork** and create a pull request:

   .. code-block:: bash

      git push origin my-feature

Code Style
----------

- Follow PEP 8 for Python code style.
- Use Sphinx autodoc docstrings (reStructuredText) for documentation.
- Ensure all public methods and classes are documented.

Documentation
-------------

Update documentation in the ``docs`` folder when adding features:

- Edit RST files (``usage.rst``, ``api.rst``, etc.).
- Add entries to ``CHANGELOG.rst`` under the appropriate version.

Run Sphinx to build docs locally:

.. code-block:: bash

   cd docs
   pip install sphinx
   make html

Open ``docs/_build/html/index.html`` to view the generated documentation.

Issues and Feedback
-------------------

Report bugs or suggest features by opening an issue on the project's repository
(if applicable) or contacting the maintainer directly.
