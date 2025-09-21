Development Guide
=================

This guide covers the development setup, workflows, and best practices for contributing to the Text Processing Toolkit.

Environment Setup
-----------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.12 or higher
* UV package manager
* Git

Installation
~~~~~~~~~~~~

1. Clone the repository:

.. code-block:: console

    $ git clone <repository-url>
    $ cd text-processing-toolkit

2. Install dependencies:

.. code-block:: console

    $ uv sync --all-groups

3. Activate the virtual environment:

.. code-block:: console

    $ source .venv/bin/activate  # On Windows: .venv\Scripts\activate

Development Workflow
--------------------

Project Structure
~~~~~~~~~~~~~~~~~

The project follows the Polylith architecture:

.. code-block:: text

    text-processing-toolkit/
    ├── components/          # Reusable components
    ├── bases/              # Application entry points
    ├── projects/           # Deployable applications
    ├── development/        # Development environment
    ├── test/               # Test suites
    ├── docs/               # Documentation
    ├── pyproject.toml      # Project configuration
    └── workspace.toml      # Polylith workspace configuration

Creating Components
~~~~~~~~~~~~~~~~~~~

1. Use the Polylith CLI to create a new component:

.. code-block:: console

    $ polylith create component my-component

2. Implement the component logic in the generated files
3. Add comprehensive tests
4. Update documentation

Running Tests
~~~~~~~~~~~~~

Run all tests:

.. code-block:: console

    $ pytest

Run specific test suites:

.. code-block:: console

    $ pytest test/components/text-core/
    $ pytest test/integration/

Run tests with coverage:

.. code-block:: console

    $ pytest --cov=components --cov-report=html

Code Quality
~~~~~~~~~~~~

Format code:

.. code-block:: console

    $ black .
    $ ruff format

Lint code:

.. code-block:: console

    $ ruff check
    $ mypy .

Type Checking
~~~~~~~~~~~~~

The project uses comprehensive type annotations. Run type checking:

.. code-block:: console

    $ mypy components/ bases/ projects/

Configuration Management
-------------------------

The project uses multiple configuration files:

Project Configuration
~~~~~~~~~~~~~~~~~~~~

``pyproject.toml`` defines:

* Project metadata
* Dependencies
* Build configuration
* Tool settings

Workspace Configuration
~~~~~~~~~~~~~~~~~~~~~~

``workspace.toml`` defines:

* Polylith workspace settings
* Component dependencies
* Build profiles

Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Environment-specific settings are managed through:

* Environment variables
* Configuration files in ``config/``
* Component-specific configuration interfaces

Testing Strategy
----------------

The project employs a comprehensive testing strategy:

Unit Tests
~~~~~~~~~~

* Test individual components in isolation
* Mock external dependencies
* Focus on business logic correctness

Integration Tests
~~~~~~~~~~~~~~~~

* Test component interactions
* Use real dependencies where appropriate
* Validate end-to-end functionality

Performance Tests
~~~~~~~~~~~~~~~~~

* Benchmark critical text processing operations
* Monitor memory usage and processing time
* Ensure scalability requirements are met

Documentation
-------------

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

Build HTML documentation:

.. code-block:: console

    $ cd docs
    $ make html

Live preview during development:

.. code-block:: console

    $ sphinx-autobuild docs/source docs/build

Documentation Standards
~~~~~~~~~~~~~~~~~~~~~~~

* Use reStructuredText for documentation
* Include docstrings for all public APIs
* Provide usage examples
* Keep documentation up-to-date with code changes

Release Process
---------------

1. **Update Version**: Increment version in ``pyproject.toml``
2. **Update Changelog**: Document changes and new features
3. **Run Full Test Suite**: Ensure all tests pass
4. **Build Documentation**: Update and build docs
5. **Create Release**: Tag and create release

Development Tools
-----------------

Recommended IDE Setup
~~~~~~~~~~~~~~~~~~~~~

* **VS Code**: With Python, Pylance, and Black extensions
* **PyCharm**: Professional or Community edition
* **Vim/Neovim**: With Python language server

Useful Commands
~~~~~~~~~~~~~~~

.. code-block:: console

    # Check workspace status
    $ polylith ws

    # Build specific project
    $ polylith build project-name

    # Check component dependencies
    $ polylith deps

Contributing
------------

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation
7. Submit a pull request

For more detailed contributing guidelines, see :doc:`contributing`.