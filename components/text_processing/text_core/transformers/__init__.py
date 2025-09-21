"""Transformer strategies for text processing.

This module implements the Strategy pattern for text transformations,
providing modular and extensible transformation capabilities.
"""

from .base_transformer import BaseTransformer, TransformerProtocol
from .basic_transformer import BasicTransformer
from .case_transformer import CaseTransformer
from .hash_transformer import HashTransformer
from .string_transformer import StringTransformer
from .json_transformer import JsonTransformer
from .line_ending_transformer import LineEndingTransformer
from .encoding_transformer import EncodingTransformer

__all__ = [
    "BaseTransformer",
    "TransformerProtocol",
    "BasicTransformer",
    "CaseTransformer",
    "HashTransformer",
    "StringTransformer",
    "JsonTransformer",
    "LineEndingTransformer",
    "EncodingTransformer",
]