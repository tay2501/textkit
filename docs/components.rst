Components
==========

The Text Processing Toolkit is built from modular components that can be combined to create powerful text processing applications. This document provides an overview of the available components and their functionality.

Available Components
--------------------

Text Core Component
~~~~~~~~~~~~~~~~~~~

**Location**: ``components/text_processing/text_core/``

The Text Core component provides fundamental text transformation capabilities including:

* **Text Transformation Engine**: Core engine for applying text transformations
* **Transformer Classes**: Strategy pattern implementation for different text operations

  * ``BasicTransformer``: Basic text operations and formatting
  * ``CaseTransformer``: Case conversion operations (upper, lower, title, etc.)
  * ``HashTransformer``: Text hashing operations for checksums and validation
  * ``StringTransformer``: Advanced string manipulation with SIMD acceleration (StringZilla)
  * ``JsonTransformer``: JSON formatting and validation operations
  * ``EncodingTransformer``: Character encoding conversions (iconv-like functionality)
  * ``JapaneseTransformer``: Japanese character width conversions (full/half-width)
  * ``LineEndingTransformer``: Line ending conversions (Unix tr-like functionality)

* **Transformation Factory**: Factory pattern for creating transformers
* **Base Classes**: Abstract base classes for implementing custom transformers
* **Type System**: Comprehensive type definitions and protocols

Key Features:
- Line ending conversion (Unix/Windows/Mac)
- Character encoding detection and conversion
- Japanese character width transformation
- Text case conversion and formatting
- Hash generation and validation
- **SIMD-Accelerated String Operations**: Hardware-optimized text processing using StringZilla
- **High-Performance Text Replacement**: Up to 10x faster than standard Python implementations
- **Memory-Efficient Processing**: Zero-copy string views and lazy iteration for large datasets

Crypto Engine Component
~~~~~~~~~~~~~~~~~~~~~~~~

**Location**: ``components/text_processing/crypto_engine/``

The Crypto Engine component provides cryptographic operations for secure text processing:

* **CryptographyManager**: Central manager for encryption/decryption operations
* **Encryption Support**: AES encryption with secure key management
* **Hash Operations**: Various hashing algorithms for data integrity
* **Secure Key Handling**: Safe key generation and management

Key Features:
- Text encryption and decryption
- Multiple hashing algorithms
- Secure random key generation
- Password-based encryption

I/O Handler Component
~~~~~~~~~~~~~~~~~~~~~

**Location**: ``components/text_processing/io_handler/``

The I/O Handler component manages input/output operations and system interactions:

* **InputOutputManager**: Centralized I/O operations management
* **Clipboard Support**: System clipboard read/write operations
* **Pipe Support**: Unix-style pipe operations for command chaining
* **File I/O**: Safe file reading and writing with error handling
* **Stream Processing**: Support for processing data streams

Key Features:
- Cross-platform clipboard operations
- Pipe-based data processing
- File system integration
- Error handling and recovery

Configuration Manager Component
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Location**: ``components/text_processing/config_manager/``

The Configuration Manager component provides centralized configuration and settings management:

* **ConfigurationManager**: Main configuration management class
* **JSON Configuration**: JSON-based configuration file support
* **Configuration Caching**: Efficient configuration loading and caching
* **Settings Validation**: Type-safe configuration validation
* **Environment Integration**: Environment variable support

Key Features:
- JSON configuration files
- Configuration validation and type checking
- Caching for performance
- Environment variable integration

Component Structure
-------------------

Each component follows a standardized structure within the Text Processing namespace:

.. code-block:: text

    components/text_processing/
    └── component-name/
        ├── __init__.py          # Public API and exports
        ├── core.py              # Main component logic
        ├── types.py             # Type definitions (if applicable)
        ├── [component-specific modules]
        └── __pycache__/         # Python bytecode cache

**Example - Text Core Component Structure:**

.. code-block:: text

    components/text_processing/text_core/
    ├── __init__.py              # Public API exports
    ├── core.py                  # TextTransformationEngine
    ├── types.py                 # Type definitions and protocols
    ├── models.py                # Data models
    ├── transformation_base.py   # Base classes for transformers
    ├── transformers/            # Transformer implementations
    │   ├── __init__.py
    │   ├── base_transformer.py
    │   ├── basic_transformer.py
    │   ├── case_transformer.py
    │   ├── encoding_transformer.py
    │   ├── japanese_transformer.py
    │   ├── line_ending_transformer.py
    │   └── string_transformer.py
    └── factories/               # Factory pattern implementations
        ├── __init__.py
        └── transformation_factory.py

Component Interfaces
--------------------

Components expose clean interfaces for interaction:

Public API
~~~~~~~~~~

Each component defines:

* **Core Functions**: Primary component functionality
* **Configuration Interface**: Component setup and configuration
* **Event Interface**: Component lifecycle events
* **Error Handling**: Standardized error responses

Dependency Management
~~~~~~~~~~~~~~~~~~~~~

Components declare their dependencies explicitly:

* **Required Dependencies**: Must be available for component to function
* **Optional Dependencies**: Enhance functionality when available
* **Interface Dependencies**: Other components this component depends on

Using Components
----------------

Components can be used in several ways:

Direct Import
~~~~~~~~~~~~~

.. code-block:: python

    from components.text_core import TextProcessor

    processor = TextProcessor()
    result = processor.process_text("input text")

Dependency Injection
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from components.text_core.interfaces import ITextProcessor

    def create_application(text_processor: ITextProcessor):
        # Use the text processor interface
        pass

Configuration-Based
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from components.config_utils import ComponentLoader

    loader = ComponentLoader()
    processor = loader.load_component("text_processor")

Component Development
---------------------

When developing new components:

1. **Define Clear Interfaces**: Use abstract base classes or protocols
2. **Implement Core Logic**: Keep business logic separate from infrastructure
3. **Add Comprehensive Tests**: Test both unit and integration scenarios
4. **Document Public APIs**: Provide clear documentation for users
5. **Handle Errors Gracefully**: Define component-specific exceptions

Best Practices
--------------

* **Single Responsibility**: Each component should have one clear purpose
* **Loose Coupling**: Minimize dependencies between components
* **High Cohesion**: Keep related functionality together
* **Interface Segregation**: Define minimal, focused interfaces
* **Dependency Inversion**: Depend on abstractions, not concretions

For more information on developing components, see the :doc:`development` guide.