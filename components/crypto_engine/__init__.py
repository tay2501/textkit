"""
Crypto Engine Component - Cryptography and hashing operations.

This component provides encryption, decryption, and hashing capabilities
for secure text processing operations.

Supported Crypto Stacks:
    - X25519CryptographyManager: Modern X25519 + ChaCha20-Poly1305 (WireGuard/Signal)
    - CryptographyManager: Legacy RSA-4096 + AES-CTR (backward compatibility)
"""

from .core import CRYPTOGRAPHY_AVAILABLE, CryptographyError, CryptographyManager
from .parallel_crypto import ParallelCryptoEngine
from .x25519_crypto import X25519CryptographyManager

__all__ = [
    "CRYPTOGRAPHY_AVAILABLE",
    "CryptographyError",
    "CryptographyManager",
    "ParallelCryptoEngine",
    "X25519CryptographyManager",
]
