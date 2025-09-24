"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Generator

from tsv_translator.infrastructure.configuration import Configuration
from tsv_translator.infrastructure.logging_config import setup_logging


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_tsv_content() -> str:
    """Sample TSV content for testing."""
    return """Name	Age	City	Score
Alice	25	Tokyo	85.5
Bob	30	Osaka	92.0
Charlie	35	Kyoto	78.3
Diana	28	Nagoya	89.7"""


@pytest.fixture
def sample_tsv_file(temp_dir: Path, sample_tsv_content: str) -> Path:
    """Create a sample TSV file for testing."""
    tsv_file = temp_dir / "sample.tsv"
    tsv_file.write_text(sample_tsv_content, encoding='utf-8')
    return tsv_file


@pytest.fixture
def test_config() -> Configuration:
    """Test configuration with safe defaults."""
    return Configuration(
        log_level='DEBUG',
        enable_console_logging=False,  # Disable during tests
        enable_file_logging=False,     # Disable during tests
        max_file_size=1_000_000,      # 1MB for tests
        preview_lines=3,
    )


@pytest.fixture
def config_with_logging(temp_dir: Path) -> Configuration:
    """Test configuration with file logging enabled."""
    log_file = temp_dir / "test.log"
    config = Configuration(
        log_level='DEBUG',
        enable_console_logging=False,
        enable_file_logging=True,
        log_file_path=str(log_file),
    )
    setup_logging(config)
    return config


@pytest.fixture
def japanese_text_samples() -> dict[str, str]:
    """Sample Japanese text for width conversion testing."""
    return {
        'full_width': 'ＡＢＣａｂｃ１２３！＠＃',
        'half_width': 'ABCabc123!@#',
        'mixed': 'ABCａｂｃ123！＠＃',
        'katakana_full': 'アイウエオカキクケコ',
        'katakana_half': 'ｱｲｳｴｵｶｷｸｹｺ',
        'hiragana': 'あいうえおかきくけこ',
    }


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before each test."""
    # Store original values
    original_env = {}
    test_env_vars = [var for var in os.environ.keys() if var.startswith('TSV_TRANSLATOR_')]

    for var in test_env_vars:
        original_env[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]

    yield

    # Restore original values
    for var, value in original_env.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]