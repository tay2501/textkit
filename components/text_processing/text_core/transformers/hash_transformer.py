"""Hash and encoding transformation strategies."""

import base64
import hashlib

from ..types import TransformationRule, TransformationRuleType
from .base_transformer import BaseTransformer


class HashTransformer(BaseTransformer):
    """Transformer for hashing and encoding operations."""

    def _initialize_rules(self) -> None:
        """Initialize hash and encoding transformation rules."""
        self._rules = {
            "sha256": TransformationRule(
                name="SHA256",
                description="Generate SHA256 hash",
                example="'hello' -> 'hash...'",
                function=self._sha256_hash,
                rule_type=TransformationRuleType.ADVANCED,
            ),
            "b64e": TransformationRule(
                name="Base64 Encode",
                description="Encode text to Base64",
                example="'hello' -> 'aGVsbG8='",
                function=self._base64_encode,
                rule_type=TransformationRuleType.ADVANCED,
            ),
            "b64d": TransformationRule(
                name="Base64 Decode",
                description="Decode Base64 text",
                example="'aGVsbG8=' -> 'hello'",
                function=self._base64_decode,
                rule_type=TransformationRuleType.ADVANCED,
            ),
        }

    def _sha256_hash(self, text: str) -> str:
        """Generate SHA256 hash of the text."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def _base64_encode(self, text: str) -> str:
        """Encode text to Base64."""
        try:
            # Use UTF-8 encoding for consistency
            encoded_bytes = text.encode('utf-8')
            base64_bytes = base64.b64encode(encoded_bytes)
            return base64_bytes.decode('ascii')
        except Exception as e:
            raise ValueError(f"Base64 encoding failed: {e}") from e

    def _base64_decode(self, text: str) -> str:
        """Decode Base64 text."""
        try:
            # Remove any whitespace/newlines and decode
            clean_text = ''.join(text.split())
            decoded_bytes = base64.b64decode(clean_text)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Base64 decoding failed: {e}") from e