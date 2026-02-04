Architecture
============

The Text Processing Toolkit is built using the Polylith architecture, which provides a unique approach to organizing code that promotes reusability, maintainability, and scalability.

Polylith Architecture
---------------------

Polylith is a software architecture that uses a monorepo to store loosely coupled components. The key benefits include:

* **Component Reusability**: Components can be shared across multiple projects
* **Independent Development**: Teams can work on different components independently
* **Simplified Testing**: Test components in isolation or integration
* **Gradual Migration**: Easy to refactor and evolve the codebase

Workspace Structure
-------------------

The workspace is organized into several key directories:

Components
~~~~~~~~~~

The ``components/`` directory contains reusable business logic components. Each component:

* Has a single responsibility
* Can be used by multiple projects
* Contains its own tests
* Has clear interfaces and dependencies

The toolkit includes 11 components:

* **async_core**: Async text transformation engine
* **command_handler**: Command processing patterns
* **common_utils**: Shared utility functions
* **config_manager**: Configuration management
* **crypto_engine**: Cryptographic operations
* **dependency_injection**: Lagom-based DI container
* **exceptions**: Hierarchical exception system
* **help_system**: Help content management
* **io_handler**: I/O operations
* **rule_parser**: Transformation rule parsing
* **text_core**: Core text transformation

Bases
~~~~~

The ``bases/`` directory contains application entry points. Bases:

* Provide the main entry point for applications
* Handle configuration and startup logic
* Wire together components to create applications

The toolkit includes 2 bases:

* **cli_interface**: Command-line interface entry point
* **interactive_session**: Interactive session management

Projects
~~~~~~~~

The ``projects/`` directory contains deployable applications. Projects:

* Combine bases and components
* Define specific deployment configurations
* Include project-specific documentation

The toolkit includes 5 projects:

* **crypto_processor**: Cryptographic text processing
* **encoding_specialist**: Character encoding operations
* **format_converter**: Format conversion utilities
* **text_transformer**: General text transformation
* **tsv_translator**: TSV translation utilities

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~

The ``development/`` directory provides:

* Development-specific configurations
* Local testing utilities
* Development documentation

Data Flow
---------

The typical data flow in the Text Processing Toolkit follows this pattern:

1. **Input Processing**: Raw text data enters through base applications
2. **Component Pipeline**: Data flows through various processing components
3. **Transformation**: Components apply specific text transformations with optional SIMD acceleration
4. **Output Generation**: Processed data is formatted and delivered

Performance Optimization
-------------------------

The toolkit implements multiple performance optimization strategies:

**SIMD Acceleration with StringZilla**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

StringZilla integration provides hardware-accelerated string operations:

* **SIMD Instructions**: Leverages AVX-512, NEON for parallel processing
* **Zero-Copy Operations**: Memory-efficient string views and lazy iteration
* **Fallback Compatibility**: Graceful degradation to standard Python implementations
* **Performance Gains**: Up to 10x faster string operations on supported hardware

**Optimized Components**
~~~~~~~~~~~~~~~~~~~~~~~~

* **String Transformer**: SIMD-accelerated text replacement and SQL list generation
* **Memory Management**: Efficient processing of large datasets (160K+ characters)
* **Hardware Detection**: Automatic SIMD capability detection and optimization

Component Dependencies
----------------------

Components are organized into a layered architecture with clear dependency boundaries:

**Core Layer**
~~~~~~~~~~~~~~

Foundation components with no internal dependencies:

* **exceptions**: Hierarchical exception system for consistent error handling
* **common_utils**: Shared utility functions used across all layers

**Infrastructure Layer**
~~~~~~~~~~~~~~~~~~~~~~~~

Components providing infrastructure services, depending only on the Core layer:

* **config_manager**: Configuration management and validation
* **io_handler**: I/O operations for file and stream handling
* **dependency_injection**: Lagom-based DI container for component wiring

**Business Layer**
~~~~~~~~~~~~~~~~~~

Components implementing core business logic, depending on Core and Infrastructure layers:

* **text_core**: Core text transformation algorithms
* **crypto_engine**: Cryptographic operations and key management
* **rule_parser**: Transformation rule parsing and execution
* **async_core**: Async text transformation engine for concurrent processing

**Application Layer**
~~~~~~~~~~~~~~~~~~~~~

Components providing application-level services, depending on all lower layers:

* **command_handler**: Command processing patterns and dispatch
* **help_system**: Help content management and display

This layered architecture ensures that components remain loosely coupled and highly testable.

Configuration Management
-------------------------

Configuration is managed through multiple layers:

* **Pydantic Settings**: Type-safe settings with validation
* **Environment-specific Configuration**: Environment variables and config files
* **Component-level Configuration**: Component-specific configuration interfaces
* **Runtime Configuration Validation**: Automatic validation on application startup
* **Type-safe Configuration Objects**: Full type hints for configuration

Dependency Injection
--------------------

The toolkit uses **Lagom** for dependency injection:

* **Explicit Dependencies**: Clear component dependencies through constructor injection
* **Container-based Wiring**: Centralized dependency management
* **Testability**: Easy mocking and testing with dependency injection
* **Lifecycle Management**: Proper initialization and cleanup of dependencies

For more details on development practices, see the :doc:`development` guide.
