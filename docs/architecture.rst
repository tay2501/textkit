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

Bases
~~~~~

The ``bases/`` directory contains application entry points. Bases:

* Provide the main entry point for applications
* Handle configuration and startup logic
* Wire together components to create applications

Projects
~~~~~~~~

The ``projects/`` directory contains deployable applications. Projects:

* Combine bases and components
* Define specific deployment configurations
* Include project-specific documentation

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

Components are designed to have minimal dependencies:

* **Core Components**: Fundamental text processing utilities
* **Processing Components**: Specific text transformation logic
* **Integration Components**: External system integrations
* **Utility Components**: Common helper functions

This architecture ensures that components remain loosely coupled and highly testable.

Configuration Management
-------------------------

Configuration is managed through:

* Environment-specific configuration files
* Component-level configuration interfaces
* Runtime configuration validation
* Type-safe configuration objects

For more details on development practices, see the :doc:`development` guide.