"""Transformer strategies for text processing.

This module implements the Strategy pattern for text transformations,
providing modular and extensible transformation capabilities.

Lazy Loading:
    Concrete transformer classes are loaded on first access via __getattr__
    to avoid importing heavy dependencies (charset_normalizer, structlog, etc.)
    at module load time. BaseTransformer and TransformerProtocol are always
    available since they have no heavy dependencies.
"""

from .base_transformer import BaseTransformer, TransformerProtocol

# Mapping of lazy-loaded class names to their module paths
_LAZY_IMPORTS: dict[str, str] = {
    "BasicTransformer": ".basic_transformer",
    "CaseTransformer": ".case_transformer",
    "EncodingTransformer": ".encoding_transformer",
    "HashTransformer": ".hash_transformer",
    "JapaneseTransformer": ".japanese_transformer",
    "JsonTransformer": ".json_transformer",
    "LineEndingTransformer": ".line_ending_transformer",
    "SqlInClauseFormatter": ".sql_formatter",
    "StringTransformer": ".string_transformer",
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        import importlib

        module = importlib.import_module(_LAZY_IMPORTS[name], __package__)
        cls = getattr(module, name)
        # Cache on the module to avoid repeated lookups
        globals()[name] = cls
        return cls
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BaseTransformer",
    "BasicTransformer",
    "CaseTransformer",
    "EncodingTransformer",
    "HashTransformer",
    "JapaneseTransformer",
    "JsonTransformer",
    "LineEndingTransformer",
    "SqlInClauseFormatter",
    "StringTransformer",
    "TransformerProtocol",
]
