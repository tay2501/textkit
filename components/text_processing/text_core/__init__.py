"""
Text Core Component - Basic text transformation engine.

This component provides fundamental text transformation capabilities
including types, base classes, and format transformations.
"""

from .types import (
    ConfigDict,
    TransformationRule,
    TransformationRuleType,
    TSVConversionOptions,
    SessionState,
    CommandResult,
    ConfigManagerProtocol,
    IOManagerProtocol,
    TransformationEngineProtocol,
    CryptoManagerProtocol,
    TransformerProtocol,
    TransformationFactoryProtocol,
)

from .transformation_base import (
    TransformationBase,
    TextTransformerProtocol,
    ConfigurableTransformerProtocol,
    ChainableTransformationBase,
    ValidationError,
    TransformationError,
)

from .core import TextTransformationEngine

# Strategy pattern components
from .transformers import (
    BaseTransformer,
    BasicTransformer,
    CaseTransformer,
    HashTransformer,
    StringTransformer,
    JsonTransformer,
)

from .factories import TransformationFactory

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
