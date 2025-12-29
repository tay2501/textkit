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
    # Strategy pattern components
    "BaseTransformer",
    "BasicTransformer",
    "CaseTransformer",
    "ChainableTransformationBase",
    "CommandResult",
    # Types and protocols
    "ConfigDict",
    "ConfigManagerProtocol",
    "ConfigurableTransformerProtocol",
    "CryptoManagerProtocol",
    "HashTransformer",
    "IOManagerProtocol",
    "JsonTransformer",
    "SessionState",
    "StringTransformer",
    "TSVConversionOptions",
    # Core engine
    "TextTransformationEngine",
    "TextTransformerProtocol",
    # Base classes and exceptions
    "TransformationBase",
    "TransformationEngineProtocol",
    "TransformationError",
    "TransformationFactory",
    "TransformationFactoryProtocol",
    "TransformationRule",
    "TransformationRuleType",
    "TransformerProtocol",
    "ValidationError",
]
