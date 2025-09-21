# Deployment Guide

This guide covers building, packaging, and deploying applications from the Text Processing Toolkit using the Polylith architecture.

## 🏗️ Build System Overview

The Text Processing Toolkit uses a modern Python build system with:

- **Build Backend**: Hatchling with `hatch-polylith-bricks` plugin
- **Package Manager**: UV for dependency management
- **Workspace Management**: Polylith workspace configuration
- **Distribution**: PyPI-compatible packages

## 📦 Project Structure for Deployment

### Workspace Configuration

```toml
# workspace.toml
[workspace]
namespace = "text_processing"
git_tag_pattern = "text_processing-{version}"
theme = "loose"

[development]
stable = "text_processing"
release = "text_processing"

[workspace.brick_docs_enabled]
enabled = false
```

### Main Project Configuration

```toml
# pyproject.toml (workspace root)
[build-system]
requires = ["hatchling", "hatch-polylith-bricks"]
build-backend = "hatchling.build"

[project]
name = "text-processing-toolkit"
version = "1.0.0"
description = "Modular text processing toolkit with Polylith architecture"
authors = [{name = "Development Team", email = "dev@example.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.12"

dependencies = [
    "typer>=0.16.1",
    "rich>=14.1.0",
    "pyperclip>=1.9.0",
    "watchdog>=6.0.0",
    "cryptography>=45.0.6",
    "sqlalchemy>=2.0.43",
    "structlog>=25.4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.4.1",
    "pytest-cov>=6.2.1",
    "mypy>=1.17.1",
    "black>=24.0.0",
    "ruff>=0.6.0",
    "polylith-cli>=1.35.0",
]

[tool.hatch.build]
dev-mode-dirs = ["components", "bases", "development", "."]

[tool.uv.workspace]
members = [
    "projects/text_transformer",
    "projects/crypto_processor",
    "projects/encoding_specialist",
    "projects/format_converter",
    "projects/tsv_translator",
]
```

## 🎯 Individual Project Deployment

Each project in the `projects/` directory can be built and deployed independently.

### Text Transformer Project

```toml
# projects/text_transformer/pyproject.toml
[build-system]
requires = ["hatchling", "hatch-polylith-bricks"]
build-backend = "hatchling.build"

[project]
name = "text-transformer"
version = "1.0.0"
description = "Text transformation CLI application"
dependencies = [
    "typer>=0.16.1",
    "rich>=14.1.0",
    "pyperclip>=1.9.0",
]

[project.scripts]
text-transformer = "text_processing.cli_interface.main:main"

[tool.polylith.build]
top-namespace = "text_processing"

[tool.polylith.bricks]
"../../bases/text_processing/cli_interface" = "text_processing/cli_interface"
"../../components/text_processing/text_core" = "text_processing/text_core"
"../../components/text_processing/io_handler" = "text_processing/io_handler"
"../../components/text_processing/config_manager" = "text_processing/config_manager"
```

### Crypto Processor Project

```toml
# projects/crypto_processor/pyproject.toml
[build-system]
requires = ["hatchling", "hatch-polylith-bricks"]
build-backend = "hatchling.build"

[project]
name = "crypto-processor"
version = "1.0.0"
description = "Cryptographic text processing application"
dependencies = [
    "typer>=0.16.1",
    "rich>=14.1.0",
    "cryptography>=45.0.6",
]

[project.scripts]
crypto-processor = "text_processing.cli_interface.main:main"

[tool.polylith.build]
top-namespace = "text_processing"

[tool.polylith.bricks]
"../../bases/text_processing/cli_interface" = "text_processing/cli_interface"
"../../components/text_processing/crypto_engine" = "text_processing/crypto_engine"
"../../components/text_processing/io_handler" = "text_processing/io_handler"
"../../components/text_processing/config_manager" = "text_processing/config_manager"
```

## 🔨 Building Projects

### Local Development Builds

```bash
# Build all projects in workspace
uv build

# Build specific project
uv build --project projects/text_transformer

# Build with specific output directory
uv build --project projects/text_transformer --out-dir dist/text_transformer
```

### Production Builds

```bash
# Clean build environment
rm -rf dist/ build/ *.egg-info/

# Build production packages
for project in projects/*/; do
    echo "Building $(basename $project)..."
    uv build --project "$project" --out-dir "dist/$(basename $project)"
done

# Verify built packages
ls -la dist/*/
```

### Build with Hatch (Alternative)

```bash
# Using hatch directly for individual projects
cd projects/text_transformer
hatch build

# Build with custom target
hatch build --target wheel

# Build all projects
for project in text_transformer crypto_processor encoding_specialist format_converter tsv_translator; do
    echo "Building $project..."
    cd "projects/$project"
    hatch build
    cd "../.."
done
```

## 📋 Build Verification

### Package Content Verification

```bash
# Inspect wheel contents
unzip -l dist/text_transformer/text_transformer-1.0.0-py3-none-any.whl

# Check package structure
python -m zipfile -l dist/text_transformer/text_transformer-1.0.0-py3-none-any.whl
```

### Installation Testing

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from wheel
pip install dist/text_transformer/text_transformer-1.0.0-py3-none-any.whl

# Test installation
text-transformer --help
python -c "import text_processing.text_core; print('Import successful')"

# Cleanup
deactivate
rm -rf test_env
```

## 🚀 Distribution Strategies

### PyPI Distribution

#### 1. Prepare for PyPI Upload

```bash
# Install distribution tools
uv add --dev twine

# Build all projects for distribution
./scripts/build_all.sh

# Check package quality
uv run twine check dist/*/*.whl dist/*/*.tar.gz
```

#### 2. Upload to Test PyPI

```bash
# Upload to Test PyPI first
uv run twine upload --repository testpypi dist/*/*.whl dist/*/*.tar.gz

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ text-transformer
```

#### 3. Upload to Production PyPI

```bash
# Upload to production PyPI
uv run twine upload dist/*/*.whl dist/*/*.tar.gz
```

### GitHub Releases

#### 1. Automated Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'

    - name: Install UV
      run: pip install uv

    - name: Install dependencies
      run: uv sync

    - name: Build packages
      run: |
        for project in projects/*/; do
          uv build --project "$project" --out-dir "dist/$(basename $project)"
        done

    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        files: dist/*/*.whl
        generate_release_notes: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    - name: Upload to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        uv add --dev twine
        uv run twine upload dist/*/*.whl
```

### Docker Deployment

#### 1. Multi-stage Dockerfile

```dockerfile
# Dockerfile.text_transformer
FROM python:3.13-slim as builder

# Install UV
RUN pip install uv

# Copy source code
COPY . /workspace
WORKDIR /workspace

# Build the specific project
RUN uv build --project projects/text_transformer --out-dir /dist

# Production stage
FROM python:3.13-slim

# Install built package
COPY --from=builder /dist/*.whl /tmp/
RUN pip install /tmp/*.whl && rm /tmp/*.whl

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Set entrypoint
ENTRYPOINT ["text-transformer"]
CMD ["--help"]
```

#### 2. Docker Compose for Multiple Services

```yaml
# docker-compose.yml
version: '3.8'

services:
  text-transformer:
    build:
      context: .
      dockerfile: Dockerfile.text_transformer
    volumes:
      - ./data:/home/app/data
    environment:
      - TEXT_PROCESSING_CONFIG=/home/app/data/config.json

  crypto-processor:
    build:
      context: .
      dockerfile: Dockerfile.crypto_processor
    volumes:
      - ./data:/home/app/data
    environment:
      - CRYPTO_CONFIG=/home/app/data/crypto_config.json

  encoding-specialist:
    build:
      context: .
      dockerfile: Dockerfile.encoding_specialist
    volumes:
      - ./data:/home/app/data
```

#### 3. Build All Docker Images

```bash
#!/bin/bash
# scripts/build_docker.sh

set -e

PROJECTS=("text_transformer" "crypto_processor" "encoding_specialist" "format_converter" "tsv_translator")

for project in "${PROJECTS[@]}"; do
    echo "Building Docker image for $project..."

    docker build \
        -f "Dockerfile.$project" \
        -t "text-processing-toolkit/$project:latest" \
        -t "text-processing-toolkit/$project:$(git describe --tags --always)" \
        .

    echo "Built text-processing-toolkit/$project"
done

echo "All Docker images built successfully!"
```

## 🔧 Environment-Specific Deployments

### Development Environment

```bash
# Development deployment script
#!/bin/bash
# scripts/deploy_dev.sh

echo "Deploying to development environment..."

# Install in development mode
uv sync --dev

# Run development checks
uv run pytest
uv run mypy .
uv run ruff check .

# Start development server
uv run python main.py --dev-mode
```

### Staging Environment

```bash
# Staging deployment script
#!/bin/bash
# scripts/deploy_staging.sh

echo "Deploying to staging environment..."

# Build packages
uv build

# Deploy to staging server
scp dist/*/*.whl staging-server:/tmp/
ssh staging-server "
    cd /opt/text-processing-toolkit &&
    python -m venv venv &&
    source venv/bin/activate &&
    pip install /tmp/*.whl &&
    systemctl restart text-processing-services
"

echo "Staging deployment complete!"
```

### Production Environment

```bash
# Production deployment script
#!/bin/bash
# scripts/deploy_prod.sh

set -e

echo "Deploying to production environment..."

# Verify all tests pass
uv run pytest --cov=90

# Build production packages
uv build --no-dev

# Deploy with blue-green strategy
for server in prod-server-1 prod-server-2; do
    echo "Deploying to $server..."

    scp dist/*/*.whl "$server:/tmp/"
    ssh "$server" "
        cd /opt/text-processing-toolkit &&
        python -m venv venv-new &&
        source venv-new/bin/activate &&
        pip install /tmp/*.whl &&

        # Health check
        text-transformer --version &&

        # Switch to new version
        mv venv venv-old &&
        mv venv-new venv &&
        systemctl restart text-processing-services &&

        # Cleanup
        rm -rf venv-old
    "
done

echo "Production deployment complete!"
```

## 📊 Monitoring and Health Checks

### Health Check Endpoints

```python
# bases/text_processing/cli_interface/health.py
from typing import Dict, Any
import structlog

logger = structlog.get_logger(__name__)

class HealthChecker:
    """Health check functionality for deployed applications."""

    def __init__(self):
        self.checks = {
            "text_core": self._check_text_core,
            "crypto_engine": self._check_crypto_engine,
            "io_handler": self._check_io_handler,
            "config_manager": self._check_config_manager,
        }

    def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks and return results."""
        results = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }

        for check_name, check_func in self.checks.items():
            try:
                check_result = check_func()
                results["checks"][check_name] = {
                    "status": "healthy",
                    "details": check_result
                }
            except Exception as e:
                logger.error(f"Health check failed: {check_name}", error=str(e))
                results["checks"][check_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                results["status"] = "unhealthy"

        return results

    def _check_text_core(self) -> Dict[str, Any]:
        """Check text core component health."""
        from text_processing.text_core import TextTransformationEngine

        engine = TextTransformationEngine()
        test_result = engine.transform_text("test", "uppercase")

        return {
            "component": "text_core",
            "test_transformation": test_result == "TEST",
            "available_operations": len(engine.get_available_operations())
        }

    def _check_crypto_engine(self) -> Dict[str, Any]:
        """Check crypto engine component health."""
        from text_processing.crypto_engine import CryptographyManager

        crypto = CryptographyManager()
        test_data = "health_check"
        test_password = "test_password_123"

        encrypted = crypto.encrypt_text(test_data, test_password)
        decrypted = crypto.decrypt_text(encrypted, test_password)

        return {
            "component": "crypto_engine",
            "encryption_test": decrypted == test_data,
            "supported_algorithms": crypto.get_supported_algorithms()
        }
```

### Deployment Monitoring

```bash
# scripts/monitor_deployment.sh
#!/bin/bash

echo "Monitoring deployment health..."

ENDPOINTS=(
    "text-transformer"
    "crypto-processor"
    "encoding-specialist"
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo "Checking $endpoint..."

    # Run health check
    if $endpoint --health-check; then
        echo "✓ $endpoint is healthy"
    else
        echo "✗ $endpoint is unhealthy"
        exit 1
    fi
done

echo "All services are healthy!"
```

## 🔄 Rollback Procedures

### Automated Rollback Script

```bash
# scripts/rollback.sh
#!/bin/bash

set -e

BACKUP_DIR="/opt/backups/text-processing-toolkit"
CURRENT_DIR="/opt/text-processing-toolkit"

echo "Starting rollback procedure..."

# Stop services
systemctl stop text-processing-services

# Find latest backup
LATEST_BACKUP=$(ls -t "$BACKUP_DIR" | head -n1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "No backup found for rollback!"
    exit 1
fi

echo "Rolling back to: $LATEST_BACKUP"

# Backup current state
mv "$CURRENT_DIR" "$BACKUP_DIR/rollback-$(date +%Y%m%d_%H%M%S)"

# Restore from backup
cp -r "$BACKUP_DIR/$LATEST_BACKUP" "$CURRENT_DIR"

# Start services
systemctl start text-processing-services

# Verify rollback
sleep 5
if systemctl is-active --quiet text-processing-services; then
    echo "Rollback successful!"
else
    echo "Rollback failed - services not running"
    exit 1
fi
```

## 📈 Performance Optimization

### Build Optimization

```bash
# Optimize build performance
export UV_CACHE_DIR=/tmp/uv-cache
export PYTHONPATH="${PYTHONPATH}:."

# Use parallel builds
uv build --jobs 4

# Enable build caching
uv build --cache-dir ~/.cache/uv-build
```

### Distribution Size Optimization

```toml
# pyproject.toml - Exclude unnecessary files
[tool.hatch.build.targets.wheel]
exclude = [
    "test/",
    "docs/",
    "*.md",
    ".git*",
    ".github/",
    "scripts/",
]

[tool.hatch.build.targets.sdist]
include = [
    "components/",
    "bases/",
    "projects/",
    "pyproject.toml",
    "README.md",
    "LICENSE",
]
```

This deployment guide provides comprehensive coverage of building, packaging, and deploying the Text Processing Toolkit across different environments and platforms. Follow these procedures to ensure reliable and consistent deployments.