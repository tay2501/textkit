Contributing Guide
==================

Thank you for your interest in contributing to the Text Processing Toolkit! This guide outlines the process for contributing and the standards we maintain.

Getting Started
---------------

Before You Begin
~~~~~~~~~~~~~~~~

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment as described in :doc:`development`
4. Create a new branch for your contribution

.. code-block:: console

    $ git checkout -b feature/your-feature-name

Types of Contributions
----------------------

We welcome several types of contributions:

Code Contributions
~~~~~~~~~~~~~~~~~~

* **New Components**: Add new text processing components
* **Bug Fixes**: Fix issues in existing code
* **Performance Improvements**: Optimize existing functionality
* **Feature Enhancements**: Improve existing features

Documentation Contributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **API Documentation**: Improve docstrings and API docs
* **User Guides**: Add or improve user documentation
* **Examples**: Add usage examples and tutorials
* **README Updates**: Improve project documentation

Testing Contributions
~~~~~~~~~~~~~~~~~~~~~

* **Unit Tests**: Add tests for existing code
* **Integration Tests**: Add end-to-end testing
* **Performance Tests**: Add benchmarking tests
* **Test Infrastructure**: Improve testing tools and utilities

Development Standards
---------------------

Code Style
~~~~~~~~~~

We follow strict code style guidelines:

* **PEP 8**: Python style guide compliance
* **Black**: Automatic code formatting
* **Ruff**: Linting and code quality checks
* **Type Hints**: Comprehensive type annotations

Run formatting and linting:

.. code-block:: console

    $ black .
    $ ruff check --fix
    $ mypy .

Testing Standards
~~~~~~~~~~~~~~~~~

All contributions must include appropriate tests:

* **Unit Tests**: Test individual functions and classes
* **Integration Tests**: Test component interactions
* **Documentation Tests**: Verify documentation examples work
* **Performance Tests**: For performance-critical code

Test Coverage Requirements:

* New code must have ≥90% test coverage
* Critical components must have ≥95% coverage
* All public APIs must be tested

Documentation Standards
~~~~~~~~~~~~~~~~~~~~~~~

* **Docstrings**: Use Google-style docstrings
* **Type Annotations**: All public functions must have type hints
* **Examples**: Include usage examples in docstrings
* **API Documentation**: Auto-generated from docstrings

Example docstring format:

.. code-block:: python

    def process_text(text: str, options: ProcessingOptions) -> ProcessedText:
        """Process input text according to specified options.

        Args:
            text: The input text to process
            options: Configuration options for processing

        Returns:
            ProcessedText object containing results

        Raises:
            ProcessingError: If text cannot be processed

        Example:
            >>> processor = TextProcessor()
            >>> result = processor.process_text("Hello world", options)
            >>> print(result.processed_text)
            'Hello World'
        """

Component Development Guidelines
-------------------------------

Creating New Components
~~~~~~~~~~~~~~~~~~~~~~~

1. **Use Polylith CLI**:

.. code-block:: console

    $ polylith create component your-component-name

2. **Follow Component Structure**:

.. code-block:: text

    components/your-component/
    ├── __init__.py          # Public API exports
    ├── core.py             # Main implementation
    ├── interfaces.py       # Abstract interfaces
    ├── models.py           # Data models
    ├── exceptions.py       # Component exceptions
    ├── types.py           # Type definitions
    └── tests/             # Test suite
        ├── __init__.py
        ├── test_core.py
        ├── test_interfaces.py
        └── conftest.py

3. **Define Clear Interfaces**:

.. code-block:: python

    from abc import ABC, abstractmethod
    from typing import Protocol

    class ITextProcessor(Protocol):
        """Interface for text processing components."""

        def process(self, text: str) -> str:
            """Process the input text."""
            ...

Component Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~

* **Single Responsibility**: Each component should have one clear purpose
* **Dependency Injection**: Use interfaces for dependencies
* **Error Handling**: Define component-specific exceptions
* **Configuration**: Support configuration through interfaces
* **Logging**: Use structured logging throughout

Pull Request Process
--------------------

Before Submitting
~~~~~~~~~~~~~~~~~

1. **Run Full Test Suite**:

.. code-block:: console

    $ pytest --cov=components --cov-report=term-missing

2. **Check Code Quality**:

.. code-block:: console

    $ black --check .
    $ ruff check
    $ mypy .

3. **Update Documentation**:

.. code-block:: console

    $ cd docs && make html

4. **Update Changelog**: Add entry to ``CHANGELOG.md``

Pull Request Guidelines
~~~~~~~~~~~~~~~~~~~~~~~

* **Clear Title**: Describe what the PR does
* **Detailed Description**: Explain the changes and motivation
* **Link Issues**: Reference related issues
* **Small Changes**: Keep PRs focused and reviewable
* **Tests Included**: Ensure new code is tested

Pull Request Template:

.. code-block:: markdown

    ## Description
    Brief description of changes

    ## Type of Change
    - [ ] Bug fix
    - [ ] New feature
    - [ ] Documentation update
    - [ ] Performance improvement

    ## Testing
    - [ ] Unit tests added/updated
    - [ ] Integration tests added/updated
    - [ ] All tests pass

    ## Documentation
    - [ ] Docstrings updated
    - [ ] Documentation updated
    - [ ] Examples added

    ## Checklist
    - [ ] Code follows style guidelines
    - [ ] Self-review completed
    - [ ] Tests added for changes
    - [ ] Documentation updated

Review Process
--------------

Code Review Standards
~~~~~~~~~~~~~~~~~~~~~

All contributions go through code review:

* **Correctness**: Code works as intended
* **Design**: Follows architectural principles
* **Testing**: Adequate test coverage
* **Documentation**: Clear and comprehensive
* **Performance**: No unnecessary performance degradation

Review Timeline
~~~~~~~~~~~~~~~

* **Initial Review**: Within 2-3 business days
* **Follow-up Reviews**: Within 1-2 business days
* **Final Approval**: After all feedback addressed

Community Guidelines
--------------------

Code of Conduct
~~~~~~~~~~~~~~~

We follow a code of conduct that ensures a welcoming environment:

* **Be Respectful**: Treat all contributors with respect
* **Be Collaborative**: Work together constructively
* **Be Patient**: Understand that review takes time
* **Be Helpful**: Provide constructive feedback

Communication Channels
~~~~~~~~~~~~~~~~~~~~~~

* **GitHub Issues**: Bug reports and feature requests
* **GitHub Discussions**: General questions and discussions
* **Pull Requests**: Code review and contribution discussion

Recognition
-----------

Contributors are recognized in several ways:

* **Contributors File**: Listed in ``CONTRIBUTORS.md``
* **Release Notes**: Mentioned in release announcements
* **GitHub Recognition**: Contributor badges and statistics

Getting Help
------------

If you need help with contributing:

1. **Read Documentation**: Check existing docs first
2. **Search Issues**: Look for similar questions
3. **Ask Questions**: Open a GitHub discussion
4. **Join Community**: Participate in project discussions

Thank you for contributing to the Text Processing Toolkit!