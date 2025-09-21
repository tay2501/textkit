# Architecture Guide

This document explains the Polylith architecture implementation in the Text Processing Toolkit.

## 🏛️ Polylith Architecture Overview

The Text Processing Toolkit follows the [Polylith architecture](https://polylith.gitbook.io/), a modular architecture pattern that enables:

- **Modular Monorepo**: Share code between multiple applications
- **Component Reusability**: Business logic components can be reused across projects
- **Clear Boundaries**: Loose coupling between modules with explicit interfaces
- **Development Efficiency**: Incremental builds and targeted testing

## 🧩 Architecture Components

### Workspace Structure

```
text-processing-toolkit/          # Workspace root
├── workspace.toml                 # Polylith workspace configuration
├── pyproject.toml                 # Main project configuration
├── components/                    # Shared business logic
├── bases/                         # Application entry points
├── projects/                      # Deployable applications
└── development/                   # Development environment
```

### 1. Components (Business Logic)

Components contain reusable business logic with no external dependencies on other components.

#### `text_core` Component
**Purpose**: Core text transformation operations
**Location**: `components/text_processing/text_core/`

```python
# Core transformation engine
class TextTransformationEngine:
    def transform_text(self, text: str, operation: str) -> str
    def apply_transformations(self, text: str, operations: List[str]) -> str

# Transformation implementations
class TextFormatTransformations:
    def to_uppercase(self, text: str) -> str
    def to_lowercase(self, text: str) -> str
    def to_title_case(self, text: str) -> str
```

#### `crypto_engine` Component
**Purpose**: Cryptographic operations and security
**Location**: `components/text_processing/crypto_engine/`

```python
# Main cryptography manager
class CryptographyManager:
    def encrypt_text(self, text: str, password: str) -> str
    def decrypt_text(self, encrypted_text: str, password: str) -> str
    def generate_hash(self, text: str, algorithm: str) -> str

# Specialized transformations
class CryptoTransformations:
    def symmetric_encrypt(self, data: bytes, key: bytes) -> bytes
    def asymmetric_encrypt(self, data: bytes, public_key) -> bytes
```

#### `io_handler` Component
**Purpose**: Input/output operations and data management
**Location**: `components/text_processing/io_handler/`

```python
# I/O operations manager
class IOManager:
    def read_file(self, filepath: str) -> str
    def write_file(self, filepath: str, content: str) -> None
    def read_from_clipboard(self) -> str
    def write_to_clipboard(self, content: str) -> None
```

#### `config_manager` Component
**Purpose**: Configuration and settings management
**Location**: `components/text_processing/config_manager/`

```python
# Configuration management
class ConfigManager:
    def load_config(self, config_path: str) -> Dict[str, Any]
    def save_config(self, config: Dict[str, Any], path: str) -> None
    def get_setting(self, key: str, default: Any = None) -> Any
```

### 2. Bases (Entry Points)

Bases provide application entry points and compose components to create functionality.

#### `cli_interface` Base
**Purpose**: Command-line interface implementation
**Location**: `bases/text_processing/cli_interface/`

```python
# Main CLI application
class CLIApplication:
    def __init__(self):
        self.text_engine = TextTransformationEngine()
        self.crypto_manager = CryptographyManager()
        self.io_manager = IOManager()

    def run_cli(self) -> None
        # Compose components into CLI commands
```

#### `interactive_session` Base
**Purpose**: Interactive user session management
**Location**: `bases/text_processing/interactive_session/`

```python
# Interactive session handler
class InteractiveSession:
    def start_session(self) -> None
    def handle_user_input(self, command: str) -> str
    def display_results(self, results: Any) -> None
```

### 3. Projects (Deployable Applications)

Projects are deployable applications that combine bases and components.

#### Available Projects

1. **`text_transformer`** - General text processing application
2. **`crypto_processor`** - Specialized cryptographic operations
3. **`encoding_specialist`** - Text encoding and character set handling
4. **`format_converter`** - File format conversion utilities
5. **`tsv_translator`** - TSV/CSV processing and transformation

Each project has its own `pyproject.toml` with specific dependencies and build configuration.

## 🔄 Data Flow

```
User Input → Base (Entry Point) → Components (Business Logic) → Output
```

### Example: Text Transformation Flow

1. **User Input**: CLI command `transform --text "hello" --operation uppercase`
2. **Base Processing**: `cli_interface` parses command and parameters
3. **Component Logic**: `text_core.TextTransformationEngine.transform_text()`
4. **Output**: Transformed text returned to user

### Example: File Encryption Flow

1. **User Input**: File path and encryption password
2. **Base Processing**: `cli_interface` validates input
3. **I/O Component**: `io_handler` reads file content
4. **Crypto Component**: `crypto_engine` encrypts content
5. **I/O Component**: `io_handler` writes encrypted file
6. **Output**: Success confirmation

## 🏗️ Build System Integration

### Hatch Integration

The project uses `hatch-polylith-bricks` plugin for Polylith-aware builds:

```toml
[build-system]
requires = ["hatchling", "hatch-polylith-bricks"]
build-backend = "hatchling.build"

[tool.hatch.build]
dev-mode-dirs = ["components", "bases", "development", "."]

[tool.polylith.build]
top-namespace = "text_processing"
```

### UV Integration

UV workspace configuration in `pyproject.toml`:

```toml
[tool.uv.workspace]
members = [
    "projects/text_transformer",
    "projects/crypto_processor",
    "projects/encoding_specialist",
    "projects/format_converter",
    "projects/tsv_translator"
]
```

## 🧪 Testing Strategy

### Component Testing
Each component has isolated unit tests:
```
test/components/text_processing/
├── text_core/test_core.py
├── crypto_engine/test_core.py
├── io_handler/test_core.py
└── config_manager/test_core.py
```

### Integration Testing
Bases are tested with component integration:
```
test/bases/text_processing/
├── cli_interface/test_core.py
└── interactive_session/test_core.py
```

### Test Execution
```bash
# Run all tests
uv run pytest

# Test specific component
uv run pytest test/components/text_processing/text_core/

# Test with coverage
uv run pytest --cov=components --cov=bases
```

## 🔧 Development Workflow

### Adding New Components

1. Create component structure:
```bash
mkdir -p components/text_processing/new_component
touch components/text_processing/new_component/__init__.py
touch components/text_processing/new_component/core.py
```

2. Implement component interface:
```python
# components/text_processing/new_component/core.py
class NewComponentManager:
    """Component following single responsibility principle."""

    def primary_operation(self, input_data: str) -> str:
        """Main component operation."""
        try:
            # EAFP style implementation
            return self._process_data(input_data)
        except Exception as e:
            # Handle gracefully
            raise ComponentError(f"Processing failed: {e}")
```

3. Add tests:
```bash
mkdir -p test/components/text_processing/new_component
touch test/components/text_processing/new_component/test_core.py
```

4. Update documentation and type hints

### Component Design Principles

1. **Single Responsibility**: Each component has one clear purpose
2. **Loose Coupling**: Components don't depend on other components
3. **High Cohesion**: Related functionality grouped together
4. **EAFP Style**: "Easier to Ask for Forgiveness than Permission"
5. **Type Safety**: Full type hints for all public interfaces

## 📊 Dependency Management

### Component Dependencies
Components can only depend on:
- Python standard library
- External packages (specified in workspace `pyproject.toml`)
- **NOT** other components (maintains loose coupling)

### Base Dependencies
Bases can depend on:
- Components (compose functionality)
- External packages
- Other bases (with careful consideration)

### Project Dependencies
Projects specify their complete dependency tree:
```toml
# projects/text_transformer/pyproject.toml
[project]
dependencies = [
    "typer>=0.16.1",
    "rich>=14.1.0",
    # Components are included via build system
]
```

## 🎯 Best Practices

### Component Development
- Keep components stateless when possible
- Use dependency injection for external resources
- Implement comprehensive error handling
- Provide clear, typed interfaces
- Write docstrings for all public methods

### Base Development
- Focus on orchestration, not business logic
- Keep UI/CLI concerns separate from business logic
- Use components for all significant operations
- Handle user input validation and error presentation

### Project Configuration
- Specify minimal dependencies
- Use semantic versioning
- Include comprehensive metadata
- Configure appropriate entry points

This architecture enables scalable development while maintaining code quality and reusability across the entire text processing toolkit.