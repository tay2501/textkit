Overview
========

The Text Processing Toolkit is a modular and extensible framework designed for building text processing applications. This project utilizes the Polylith architecture to ensure high maintainability, code reusability, and token-optimized performance.

Key Features
------------

* **Modular Architecture**: Built with Polylith for maximum component reusability
* **Line Ending Conversion**: Unix tr-like line ending transformations
* **Character Encoding Conversion**: Unix iconv-like encoding transformations with auto-detection
* **SIMD-Accelerated Operations**: High-performance string processing with StringZilla
* **Japanese Text Processing**: Full-width/half-width character conversion with jaconv
* **Clipboard Management**: Cross-platform clipboard operations
* **Cryptographic Operations**: Text encryption and decryption
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
* **Typer** - Modern CLI framework with rich formatting
* **Rich** - Rich text and beautiful formatting in terminal
* **Lagom** - Dependency injection container
* **Pydantic** - Data validation and settings management
* **SQLAlchemy** - SQL toolkit and ORM
* **Structlog** - Structured logging
* **StringZilla** - SIMD-accelerated string operations
* **Jaconv** - Japanese character width conversion
* **Charset-Normalizer** - Automatic character encoding detection
* **Cryptography** - Secure cryptographic operations
* **Pyperclip** - Cross-platform clipboard operations

Getting Started
---------------

To get started with the Text Processing Toolkit, see the :doc:`development` guide for setup instructions and the :doc:`architecture` documentation for understanding the system design.