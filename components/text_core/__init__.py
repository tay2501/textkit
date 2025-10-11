"""
Text Core Component - Basic text transformation engine.

This component provides fundamental text transformation capabilities
including types, base classes, and format transformations.
"""

from .core import TextTransformationEngine
from .exceptions import TransformationError, ValidationError
from .factories import TransformationFactory
from .transformation_base import (
    ChainableTransformationBase,
    ConfigurableTransformerProtocol,
    TextTransformerProtocol,
    TransformationBase,
)

# Strategy pattern components
from .transformers import (
    BaseTransformer,
    BasicTransformer,
    CaseTransformer,
    HashTransformer,
    JsonTransformer,
    StringTransformer,
)
from .types import (
    CommandResult,
    ConfigDict,
    ConfigManagerProtocol,
    CryptoManagerProtocol,
    IOManagerProtocol,
    SessionState,
    TransformationEngineProtocol,
    TransformationFactoryProtocol,
    TransformationRule,
    TransformationRuleType,
    TransformerProtocol,
    TSVConversionOptions,
)

__all__ = [
    # Types and protocols
    "ConfigDict",
    "TransformationRule",
    "TransformationRuleType",
    "TSVConversionOptions",
    "SessionState",
    "CommandResult",
    "ConfigManagerProtocol",
    "IOManagerProtocol",
    "TransformationEngineProtocol",
    "CryptoManagerProtocol",
    "TransformerProtocol",
    "TransformationFactoryProtocol",
    # Base classes and exceptions
    "TransformationBase",
    "TextTransformerProtocol",
    "ConfigurableTransformerProtocol",
    "ChainableTransformationBase",
    "ValidationError",
    "TransformationError",
    # Core engine
    "TextTransformationEngine",
    # Strategy pattern components
    "BaseTransformer",
    "BasicTransformer",
    "CaseTransformer",
    "HashTransformer",
    "StringTransformer",
    "JsonTransformer",
    "TransformationFactory",
]
