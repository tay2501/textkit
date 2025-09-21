Overview
========

The Text Processing Toolkit is a modular and extensible framework designed for building text processing applications. This project utilizes the Polylith architecture to ensure high maintainability, code reusability, and token-optimized performance.

Key Features
------------

* **Modular Architecture**: Built with Polylith for maximum component reusability
* **Token-Optimized**: Designed for efficient processing and minimal resource usage
* **Extensible Framework**: Easy to add new components and functionality
* **Type Safety**: Full Python type annotations for better development experience
* **Comprehensive Testing**: Robust test suite with pytest

Project Structure
-----------------

The project follows the Polylith workspace structure:

* ``components/`` - Reusable business logic components
* ``bases/`` - Application entry points
* ``projects/`` - Deployable applications
* ``development/`` - Development environment
* ``test/`` - Test suites

Technology Stack
----------------

* **Python 3.12+** - Modern Python with latest features
* **UV** - Fast Python package manager and environment management
* **Typer** - Modern CLI framework
* **Rich** - Rich text and beautiful formatting
* **SQLAlchemy** - SQL toolkit and ORM
* **Structlog** - Structured logging

Getting Started
---------------

To get started with the Text Processing Toolkit, see the :doc:`development` guide for setup instructions and the :doc:`architecture` documentation for understanding the system design.