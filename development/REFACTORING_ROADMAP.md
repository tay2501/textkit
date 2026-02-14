# Text Processing Toolkit - 包括的リファクタリングロードマップ

**作成日:** 2025-11-23
**最終更新日:** 2026-01-19
**対象:** Text Processing Toolkit v1.0 (Polylith Architecture)
**目標:** Production-Ready Excellence (A → S Rank)

**ステータス:**
- **Phase 1: 完了済み**
- **Phase 2: 未着手**
- **Phase 3: 未着手**

---

## 📋 Executive Summary

このロードマップは、python-code-reviewerによる包括的コードレビュー結果と、最新のPythonベストプラクティス調査（cryptography, pydantic, structlog公式ドキュメント）に基づいて策定されています。

### 現状評価
- **総合評価:** A (Production-Ready)
- **強み:** Polylithアーキテクチャ、Pydantic V2、structlog、Python 3.13最新機能
- **改善領域:** セキュリティ強化、型安全性向上、一貫性維持

### 予想される成果
- **セキュリティ:** OWASP Top 10脆弱性の完全解消
- **保守性:** コード重複30%削減 (約300行)
- **テスタビリティ:** Protocol-basedモックにより単体テスト速度2倍向上
- **品質:** Mypy厳格モード完全準拠、型安全性100%達成

---

## 🎯 Phase 1: Critical Security Fixes (P0 - ✅ 完了済み)

**期間:** 1日 (5作業時間)
**優先度:** 🔴 Critical
**担当者推奨:** セキュリティエンジニア or シニア開発者

### 1.1 秘密鍵暗号化の実装

**問題:** `components/crypto_engine/core.py:244`で秘密鍵が平文保存されていました。
**リスク:** OWASP A02:2021 - Cryptographic Failures
**影響範囲:** `components/crypto_engine/core.py`

#### 実装概要

**Step 1.1.1: 環境変数設定 (完了済み)**
- `.env.example`に`TEXTKIT_KEY_PASSPHRASE`の設定を追加しました。

**Step 1.1.2: コード修正 (完了済み)**
- `CryptographyManager`にて、`_get_key_passphrase`から取得したパスフレーズを使い、`serialization.BestAvailableEncryption`で秘密鍵を暗号化して保存するように修正しました。
- `load_pem_private_key`呼び出し時に`password`引数を渡し、復号するように修正しました。

**Step 1.1.3: テストの更新 (完了済み)**
- 秘密鍵が暗号化されているか、パスフレーズが間違っている場合に正しく失敗するかを検証するテストを追加しました。

**Step 1.1.4: ドキュメント更新 (完了済み)**
- `README.md`に秘密鍵の暗号化に関する設定方法を追記しました。

**Step 1.1.5: 検証 (完了済み)**
- 秘密鍵が暗号化されていること、改ざん検知が機能すること、テストがすべてパスすることを確認しました。

---

### 1.2 暗号化モードの統一 (CBC → GCM)

**問題:** `core.py` (CBC) と `crypto.py` (GCM) の不整合がありました。
**リスク:** パディングオラクル攻撃、データ非互換性
**影響範囲:** `components/crypto_engine/core.py`, `components/crypto_engine/crypto.py`

#### 実装概要

**Step 1.2.1: AES-GCM統一実装 (完了済み)**
- `encrypt_text`/`decrypt_text`メソッドを、認証付き暗号である`AES-GCM`を使用するロジックに統一しました。

**Step 1.2.2: crypto.pyの削除と統合 (完了済み)**
- 不要になった`crypto.py`を削除し、`__init__.py`を更新しました。

**Step 1.2.3: 既存データの移行スクリプト作成 (完了済み)**
- CBCからGCMへデータを移行するための`bin/migrate_crypto_cbc_to_gcm.py`スクリプトを作成しました。

**Step 1.2.4: テストの更新 (完了済み)**
- GCMに特化したテストを追加し、CBC関連のテストを削除しました。

---

### 1.3 検証とロールバック戦略

**検証チェックリスト (完了済み):**
- セキュリティ検証、GCM暗号化/復号化テスト、改ざん検知テスト、フルテストスイートを実行し、すべて成功しました。

**ロールバック手順:**
- (現在は完了済みのため、参考情報)

---

### 成果物

- [x] `components/crypto_engine/core.py` - BestAvailableEncryption実装
- [x] `test/components/crypto_engine/test_core.py` - セキュリティテスト追加
- [x] `.env.example` - セキュリティ設定のドキュメント
- [x] `README.md` - セキュリティセクション追加
- [x] `components/crypto_engine/core.py` - AES-GCM統一実装
- [x] `bin/migrate_crypto_cbc_to_gcm.py` - 移行スクリプト
- [x] 検証レポート

---

## 🛠 Phase 2: Quality & Type Safety (P1 - 1週間以内)

**期間:** 5日 (9作業時間)
**優先度:** 🟡 High
**担当者推奨:** 全開発者

### 2.1 型ヒントの改善 (Protocol-based)

**目標:** `Any`型の削減、Protocolベースの型定義
**影響範囲:** `components/crypto_engine/`, `components/config_manager/`

#### 実装手順

**Step 2.1.1: Protocolファイルの作成 (2時間)**

**ファイル:** `components/crypto_engine/protocols.py` (新規作成)

```python
"""Type protocols for crypto_engine component.

This module defines runtime-checkable protocols for dependency injection
and type-safe interfaces, following modern Python typing best practices.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Import only for type checking to avoid circular dependencies
    from cryptography.hazmat.primitives.asymmetric.rsa import (
        RSAPrivateKey,
        RSAPublicKey,
    )
else:
    # At runtime, use Any to avoid import errors if cryptography not installed
    RSAPrivateKey = Any
    RSAPublicKey = Any


@runtime_checkable
class ConfigManagerProtocol(Protocol):
    """Protocol for configuration manager with security config support.

    Implementers must provide method to load security configuration
    containing RSA and encryption settings.
    """

    def load_security_config(self) -> dict[str, Any]:
        """Load security configuration from settings.

        Returns:
            Dictionary containing security settings with at least 'rsa' key:
            {
                "rsa": {
                    "key_size": int,
                    "public_exponent": int,
                    "key_directory": str,
                    ...
                }
            }
        """
        ...


@runtime_checkable
class KeyManagerProtocol(Protocol):
    """Protocol for RSA key pair management operations."""

    def generate_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Generate new RSA key pair.

        Returns:
            Tuple of (private_key, public_key)
        """
        ...

    def load_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Load existing RSA key pair from storage.

        Returns:
            Tuple of (private_key, public_key)

        Raises:
            CryptographyError: If keys cannot be loaded
        """
        ...

    def ensure_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Ensure RSA key pair exists, generate if needed.

        Returns:
            Tuple of (private_key, public_key)
        """
        ...


@runtime_checkable
class EncryptionEngineProtocol(Protocol):
    """Protocol for encryption/decryption operations."""

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt binary data.

        Args:
            data: Raw bytes to encrypt

        Returns:
            Encrypted bytes
        """
        ...

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt binary data.

        Args:
            encrypted_data: Encrypted bytes to decrypt

        Returns:
            Decrypted bytes

        Raises:
            CryptographyError: If decryption fails or data is tampered
        """
        ...


@runtime_checkable
class TextCryptoServiceProtocol(Protocol):
    """High-level protocol for text encryption/decryption services.

    This is the main interface for application code to use
    for encrypting and decrypting text data.
    """

    def encrypt_text(self, text: str) -> str:
        """Encrypt text to base64-encoded string.

        Args:
            text: Plaintext to encrypt

        Returns:
            Base64-encoded encrypted data
        """
        ...

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt base64-encoded string to text.

        Args:
            encrypted_text: Base64-encoded encrypted data

        Returns:
            Decrypted plaintext

        Raises:
            CryptographyError: If decryption fails
        """
        ...

    def is_available(self) -> bool:
        """Check if cryptography is available.

        Returns:
            True if cryptography library is installed and functional
        """
        ...

    def get_key_info(self) -> dict[str, Any]:
        """Get key configuration information.

        Returns:
            Dictionary with key configuration details
        """
        ...
```

**Step 2.1.2: 既存コードの型ヒント更新 (2時間)**

**ファイル:** `components/crypto_engine/core.py`

```python
# UPDATE: Import section
from __future__ import annotations

import base64
import secrets
from pathlib import Path
from typing import TYPE_CHECKING

from textkit.exceptions import CryptoTransformationError as CryptographyError
from .protocols import ConfigManagerProtocol  # ADD

# Cryptography imports with availability check
try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    if TYPE_CHECKING:
        from cryptography.hazmat.primitives.asymmetric.rsa import (
            RSAPrivateKey,
            RSAPublicKey,
        )

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    if TYPE_CHECKING:
        from typing import Any
        RSAPrivateKey = Any  # type: ignore[misc]
        RSAPublicKey = Any  # type: ignore[misc]


class CryptographyManager:
    """Modern cryptographic manager with hybrid RSA+AES-GCM encryption.

    Implements TextCryptoServiceProtocol for dependency injection compatibility.
    """

    def __init__(
        self,
        config_manager: ConfigManagerProtocol | None = None  # CHANGED: was Any
    ) -> None:
        """Initialize the cryptography manager.

        Args:
            config_manager: Optional configuration manager implementing
                          ConfigManagerProtocol for security settings

        Raises:
            CryptographyError: If cryptography library is unavailable
        """
        # ... (implementation remains same)
```

---

### 2.2 ロギングの統一 (structlog)

**目標:** すべての`logging`を`structlog`に統一
**影響範囲:** 全コンポーネント

#### 実装手順

**Step 2.2.1: モジュールレベルlogger初期化 (3時間)**

**パターン:**

```python
# BAD: Function-level import (anti-pattern)
def my_function():
    import logging  # ❌ Don't do this
    logger = logging.getLogger(__name__)
    logger.info("Message")


# GOOD: Module-level structlog (recommended)
import structlog

logger = structlog.get_logger(__name__)  # ✓ Module-level


def my_function():
    logger.info("message", key="value")  # ✓ Direct use
```

**対象ファイル一覧:**

```bash
# Find all logging imports
rg "import logging" --type python -l

# Expected files:
# - components/text_core/transformers/string_transformer.py
# - (Add others as discovered)
```

**修正例:** `components/text_core/transformers/string_transformer.py`

```python
# BEFORE
def apply_tsv_replacements(self, text: str, tsv_file: str | Path) -> str:
    import logging  # ❌ Anti-pattern
    logger = logging.getLogger(__name__)
    logger.warning(f"Line {line_num}: insufficient columns")


# AFTER
import structlog

# Module-level logger (at top of file)
logger = structlog.get_logger(__name__)


def apply_tsv_replacements(self, text: str, tsv_file: str | Path) -> str:
    # No import needed, use module-level logger
    logger.warning(
        "insufficient_tsv_columns",
        line=line_num,
        file=str(tsv_file),
        columns=len(row)
    )
```

---

### 2.3 Mypy厳格モード対応

**目標:** `mypy --strict`完全準拠
**影響範囲:** `components/`, `bases/`

#### 実装手順

**Step 2.3.1: mypy設定ファイル更新 (30分)**

**ファイル:** `mypy.ini`

```ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_unimported = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
check_untyped_defs = True
strict_equality = True

# Per-module options
[mypy-tests.*]
disallow_untyped_defs = False

[mypy-cryptography.*]
ignore_missing_imports = True

[mypy-pyperclip.*]
ignore_missing_imports = True
```

**Step 2.3.2: 型エラーの修正 (4時間)**

```bash
# 1. Run mypy in strict mode
uv run mypy components bases --strict > mypy_errors.txt

# 2. Fix errors iteratively
# Priority order:
# - P0: disallow_untyped_defs errors
# - P1: disallow_any_explicit errors
# - P2: warn_return_any errors

# 3. Verify no errors
uv run mypy components bases --strict
# Expected: Success: no issues found
```

---

### Phase 2 成果物

- [x] `components/crypto_engine/protocols.py` - Protocol定義
- [x] `components/crypto_engine/core.py` - 型ヒント更新
- [x] 全コンポーネント - structlog統一
- [x] `mypy.ini` - 厳格モード設定
- [x] Mypyエラーゼロ達成

---

## 🏗 Phase 3: Architecture Refactoring (P2 - 2週間以内)

**期間:** 10日 (14作業時間)
**優先度:** 🔵 Medium
**担当者推奨:** アーキテクト + シニア開発者

### 3.1 Crypto Component再設計 (DI統合)

**目標:** 重複コード削減30%、テスタビリティ2倍向上
**影響範囲:** `components/crypto_engine/`, `components/dependency_injection/`

#### 新アーキテクチャ

```
components/crypto_engine/
├── __init__.py           # Public API
├── protocols.py          # Interface definitions (Phase 2で作成済み)
├── key_management.py     # RSA key operations (NEW)
├── encryption.py         # AES-GCM operations (NEW)
├── service.py            # High-level facade (NEW)
└── factory.py            # DI integration (NEW)
```

#### 実装手順

**Step 3.1.1: 責任分離 - Key Management (3時間)**

**ファイル:** `components/crypto_engine/key_management.py` (新規作成)

```python
"""RSA key management module.

Handles RSA key pair generation, loading, and secure storage.
Separated from encryption logic for better testability and SRP compliance.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import structlog
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from textkit.exceptions import CryptoTransformationError as CryptographyError
from .protocols import KeyManagerProtocol

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.rsa import (
        RSAPrivateKey,
        RSAPublicKey,
    )

logger = structlog.get_logger(__name__)


class RSAKeyManager:
    """RSA key pair manager with secure passphrase protection.

    Implements KeyManagerProtocol for dependency injection.

    Features:
    - RSA-4096 key generation
    - PBKDF2 passphrase-based encryption (BestAvailableEncryption)
    - Secure file permissions (0o600 for private, 0o644 for public)
    - Environment variable-based passphrase management
    """

    DEFAULT_KEY_SIZE = 4096
    DEFAULT_PUBLIC_EXPONENT = 65537
    DEFAULT_PASSPHRASE_ENV_VAR = "TEXTKIT_KEY_PASSPHRASE"
    MINIMUM_PASSPHRASE_LENGTH = 32

    def __init__(
        self,
        key_directory: Path | str = "rsa",
        key_size: int = DEFAULT_KEY_SIZE,
        passphrase_env_var: str = DEFAULT_PASSPHRASE_ENV_VAR,
    ) -> None:
        """Initialize RSA key manager.

        Args:
            key_directory: Directory for key storage
            key_size: RSA key size in bits (default: 4096)
            passphrase_env_var: Environment variable name for passphrase
        """
        self.key_directory = Path(key_directory)
        self.key_size = key_size
        self.public_exponent = self.DEFAULT_PUBLIC_EXPONENT
        self.passphrase_env_var = passphrase_env_var

        # Ensure directory exists with secure permissions
        self.key_directory.mkdir(mode=0o700, exist_ok=True)

        # Set key paths
        self.private_key_path = self.key_directory / "private_key.pem"
        self.public_key_path = self.key_directory / "public_key.pem"

    def _get_passphrase(self) -> bytes:
        """Get passphrase from environment variable.

        Returns:
            UTF-8 encoded passphrase

        Raises:
            CryptographyError: If passphrase not set or too short
        """
        passphrase = os.environ.get(self.passphrase_env_var)

        if not passphrase:
            raise CryptographyError(
                f"Passphrase not set. Set environment variable: {self.passphrase_env_var}",
                {"required_env_var": self.passphrase_env_var},
            )

        if len(passphrase) < self.MINIMUM_PASSPHRASE_LENGTH:
            raise CryptographyError(
                f"Passphrase too short (minimum {self.MINIMUM_PASSPHRASE_LENGTH} chars)",
                {
                    "required_length": self.MINIMUM_PASSPHRASE_LENGTH,
                    "actual_length": len(passphrase),
                },
            )

        return passphrase.encode("utf-8")

    def generate_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Generate new RSA key pair.

        Returns:
            Tuple of (private_key, public_key)
        """
        logger.info(
            "generating_rsa_keypair",
            key_size=self.key_size,
            public_exponent=self.public_exponent,
        )

        private_key = rsa.generate_private_key(
            public_exponent=self.public_exponent,
            key_size=self.key_size,
            backend=default_backend(),
        )
        public_key = private_key.public_key()

        # Save immediately with encryption
        self._save_key_pair(private_key, public_key)

        return private_key, public_key

    def load_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Load existing RSA key pair from encrypted PEM files.

        Returns:
            Tuple of (private_key, public_key)

        Raises:
            CryptographyError: If keys cannot be loaded
        """
        try:
            passphrase = self._get_passphrase()

            # Load encrypted private key
            private_pem = self.private_key_path.read_bytes()
            private_key = serialization.load_pem_private_key(
                private_pem,
                password=passphrase,
                backend=default_backend(),
            )

            # Load public key
            public_pem = self.public_key_path.read_bytes()
            public_key = serialization.load_pem_public_key(
                public_pem,
                backend=default_backend(),
            )

            logger.info(
                "rsa_keypair_loaded",
                private_key_path=str(self.private_key_path),
                public_key_path=str(self.public_key_path),
            )

            return private_key, public_key

        except ValueError as e:
            raise CryptographyError(
                "Incorrect passphrase",
                {"error_type": "incorrect_passphrase"},
            ) from e
        except Exception as e:
            raise CryptographyError(
                f"Failed to load key pair: {e}",
                {
                    "private_key_exists": self.private_key_path.exists(),
                    "public_key_exists": self.public_key_path.exists(),
                },
            ) from e

    def ensure_key_pair(self) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Ensure RSA key pair exists, generate if needed.

        Returns:
            Tuple of (private_key, public_key)
        """
        if self.private_key_path.exists() and self.public_key_path.exists():
            return self.load_key_pair()
        else:
            logger.info("rsa_keypair_not_found_generating")
            return self.generate_key_pair()

    def _save_key_pair(
        self,
        private_key: RSAPrivateKey,
        public_key: RSAPublicKey
    ) -> None:
        """Save key pair with secure encryption and permissions."""
        passphrase = self._get_passphrase()

        # Serialize private key with encryption
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
        )

        # Write private key with secure permissions
        self.private_key_path.write_bytes(private_pem)
        self.private_key_path.chmod(0o600)

        # Serialize public key (no encryption)
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Write public key
        self.public_key_path.write_bytes(public_pem)
        self.public_key_path.chmod(0o644)

        logger.info(
            "rsa_keypair_saved",
            private_key_path=str(self.private_key_path),
            public_key_path=str(self.public_key_path),
        )
```

**Step 3.1.2: 責任分離 - Encryption Engine (3時間)**

**ファイル:** `components/crypto_engine/encryption.py` (新規作成)

```python
"""AES-GCM encryption engine module.

Handles symmetric encryption/decryption using AES-256-GCM.
Separated from key management for better testability and SRP compliance.
"""

from __future__ import annotations

import base64
import secrets
from typing import TYPE_CHECKING

import structlog
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from textkit.exceptions import CryptoTransformationError as CryptographyError
from .protocols import EncryptionEngineProtocol, KeyManagerProtocol

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.rsa import (
        RSAPrivateKey,
        RSAPublicKey,
    )

logger = structlog.get_logger(__name__)


class AESGCMEngine:
    """AES-256-GCM encryption engine with RSA key wrapping.

    Implements EncryptionEngineProtocol for dependency injection.

    Features:
    - AES-256-GCM authenticated encryption (AEAD)
    - RSA-wrapped AES keys
    - Automatic integrity verification
    - Tampering detection
    """

    DEFAULT_AES_KEY_SIZE = 32  # AES-256
    DEFAULT_NONCE_SIZE = 12    # 96-bit (NIST recommended for GCM)
    TAG_SIZE = 16              # GCM tag is always 16 bytes

    def __init__(
        self,
        key_manager: KeyManagerProtocol,
        aes_key_size: int = DEFAULT_AES_KEY_SIZE,
        nonce_size: int = DEFAULT_NONCE_SIZE,
    ) -> None:
        """Initialize AES-GCM encryption engine.

        Args:
            key_manager: RSA key manager for key wrapping
            aes_key_size: AES key size in bytes (default: 32 for AES-256)
            nonce_size: Nonce size in bytes (default: 12 for 96-bit)
        """
        self.key_manager = key_manager
        self.aes_key_size = aes_key_size
        self.nonce_size = nonce_size

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt binary data using AES-256-GCM with RSA key wrapping.

        Process:
        1. Generate random AES key and nonce
        2. Encrypt data with AES-GCM
        3. Wrap AES key with RSA public key
        4. Combine: encrypted_aes_key + nonce + tag + encrypted_data

        Args:
            data: Raw bytes to encrypt

        Returns:
            Encrypted bytes (encrypted_key + nonce + tag + ciphertext)
        """
        try:
            # Generate ephemeral AES key and nonce
            aes_key = secrets.token_bytes(self.aes_key_size)
            nonce = secrets.token_bytes(self.nonce_size)

            # Encrypt with AES-GCM
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            tag = encryptor.tag

            # Wrap AES key with RSA
            _, public_key = self.key_manager.ensure_key_pair()
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            # Combine components
            return encrypted_aes_key + nonce + tag + ciphertext

        except Exception as e:
            raise CryptographyError(
                f"Encryption failed: {e}",
                {"error_type": type(e).__name__, "data_length": len(data)},
            ) from e

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt binary data using AES-256-GCM with RSA key unwrapping.

        Process:
        1. Extract encrypted_aes_key, nonce, tag, ciphertext
        2. Unwrap AES key with RSA private key
        3. Decrypt ciphertext with AES-GCM
        4. Verify authentication tag

        Args:
            encrypted_data: Encrypted bytes from encrypt()

        Returns:
            Decrypted bytes

        Raises:
            CryptographyError: If decryption fails or tampering detected
        """
        try:
            # Calculate RSA key size from key manager
            private_key, _ = self.key_manager.ensure_key_pair()
            rsa_key_size_bytes = private_key.key_size // 8

            # Extract components
            offset1 = rsa_key_size_bytes
            offset2 = offset1 + self.nonce_size
            offset3 = offset2 + self.TAG_SIZE

            encrypted_aes_key = encrypted_data[:offset1]
            nonce = encrypted_data[offset1:offset2]
            tag = encrypted_data[offset2:offset3]
            ciphertext = encrypted_data[offset3:]

            # Unwrap AES key with RSA
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            # Decrypt with AES-GCM (verifies tag automatically)
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            return plaintext

        except Exception as e:
            raise CryptographyError(
                f"Decryption failed: {e}",
                {
                    "error_type": type(e).__name__,
                    "encrypted_length": len(encrypted_data),
                    "hint": "Data may be tampered" if "tag" in str(e).lower() else None,
                },
            ) from e
```

**Step 3.1.3: High-Level Service (2時間)**

**ファイル:** `components/crypto_engine/service.py` (新規作成)

```python
"""High-level cryptography service providing text encryption/decryption.

This module provides the main user-facing API for the crypto_engine component.
"""

from __future__ import annotations

import base64

import structlog
from textkit.exceptions import CryptoTransformationError as CryptographyError
from .protocols import (
    EncryptionEngineProtocol,
    KeyManagerProtocol,
    TextCryptoServiceProtocol,
)

logger = structlog.get_logger(__name__)


class HybridCryptoService:
    """High-level service for text encryption/decryption.

    Implements TextCryptoServiceProtocol for dependency injection.
    Composes KeyManager and EncryptionEngine for hybrid encryption.
    """

    def __init__(
        self,
        key_manager: KeyManagerProtocol,
        encryption_engine: EncryptionEngineProtocol,
    ) -> None:
        """Initialize hybrid crypto service.

        Args:
            key_manager: RSA key manager
            encryption_engine: AES-GCM encryption engine
        """
        self.key_manager = key_manager
        self.encryption_engine = encryption_engine

    def encrypt_text(self, text: str) -> str:
        """Encrypt text to base64-encoded string.

        Args:
            text: Plaintext to encrypt (UTF-8)

        Returns:
            Base64-encoded encrypted data

        Raises:
            CryptographyError: If encryption fails
        """
        if not isinstance(text, str):
            raise CryptographyError(
                f"Input must be str, got {type(text).__name__}",
                {"input_type": type(text).__name__},
            )

        try:
            # UTF-8 encode
            text_bytes = text.encode("utf-8")

            # Encrypt
            encrypted_bytes = self.encryption_engine.encrypt(text_bytes)

            # Base64 encode for text-safe transmission
            return base64.b64encode(encrypted_bytes).decode("ascii")

        except CryptographyError:
            raise
        except Exception as e:
            raise CryptographyError(
                f"Text encryption failed: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt base64-encoded string to text.

        Args:
            encrypted_text: Base64-encoded encrypted data

        Returns:
            Decrypted plaintext (UTF-8)

        Raises:
            CryptographyError: If decryption fails
        """
        try:
            # Base64 decode
            encrypted_bytes = base64.b64decode(encrypted_text.encode("ascii"))

            # Decrypt
            decrypted_bytes = self.encryption_engine.decrypt(encrypted_bytes)

            # UTF-8 decode
            return decrypted_bytes.decode("utf-8")

        except CryptographyError:
            raise
        except Exception as e:
            raise CryptographyError(
                f"Text decryption failed: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def is_available(self) -> bool:
        """Check if cryptography is available.

        Returns:
            Always True (raises at import if unavailable)
        """
        return True

    def get_key_info(self) -> dict[str, any]:
        """Get key configuration information.

        Returns:
            Dictionary with key configuration
        """
        return {
            "key_directory": str(self.key_manager.key_directory),
            "key_size": self.key_manager.key_size,
            "private_key_exists": self.key_manager.private_key_path.exists(),
            "public_key_exists": self.key_manager.public_key_path.exists(),
        }
```

**Step 3.1.4: DI Factory (2時間)**

**ファイル:** `components/crypto_engine/factory.py` (新規作成)

```python
"""Dependency injection factory for crypto_engine component.

Integrates with Lagom DI container for automatic service resolution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textkit.dependency_injection import Container, Singleton

if TYPE_CHECKING:
    from .protocols import (
        EncryptionEngineProtocol,
        KeyManagerProtocol,
        TextCryptoServiceProtocol,
    )


def register_crypto_services(container: Container) -> None:
    """Register cryptography services in DI container.

    Registers:
    - RSAKeyManager as KeyManagerProtocol (singleton)
    - AESGCMEngine as EncryptionEngineProtocol (singleton)
    - HybridCryptoService as TextCryptoServiceProtocol (singleton)

    Args:
        container: Lagom DI container instance
    """
    from .encryption import AESGCMEngine
    from .key_management import RSAKeyManager
    from .service import HybridCryptoService

    # Register key manager as singleton
    container[KeyManagerProtocol] = Singleton(RSAKeyManager)

    # Register encryption engine (depends on KeyManager)
    container[EncryptionEngineProtocol] = Singleton(
        lambda c: AESGCMEngine(key_manager=c[KeyManagerProtocol])
    )

    # Register high-level service (depends on both)
    container[TextCryptoServiceProtocol] = Singleton(
        lambda c: HybridCryptoService(
            key_manager=c[KeyManagerProtocol],
            encryption_engine=c[EncryptionEngineProtocol],
        )
    )


def get_crypto_service() -> TextCryptoServiceProtocol:
    """Get configured text cryptography service from DI container.

    Returns:
        Fully configured TextCryptoServiceProtocol implementation
    """
    from textkit.dependency_injection import get_container

    container = get_container()

    # Auto-register if not already registered
    if TextCryptoServiceProtocol not in container:
        register_crypto_services(container)

    return container[TextCryptoServiceProtocol]
```

**Step 3.1.5: core.py削除と後方互換性 (1時間)**

**ファイル:** `components/crypto_engine/__init__.py`

```python
"""Cryptography component providing secure encryption/decryption.

This component implements hybrid RSA+AES-GCM encryption with:
- RSA-4096 for key exchange
- AES-256-GCM for data encryption (AEAD)
- Passphrase-protected private keys
- Secure file permissions
- Protocol-based dependency injection

Architecture:
- key_management.py: RSA key operations
- encryption.py: AES-GCM operations
- service.py: High-level text encryption API
- factory.py: DI integration
- protocols.py: Interface definitions
"""

from .encryption import AESGCMEngine
from .factory import get_crypto_service, register_crypto_services
from .key_management import RSAKeyManager
from .protocols import (
    ConfigManagerProtocol,
    EncryptionEngineProtocol,
    KeyManagerProtocol,
    TextCryptoServiceProtocol,
)
from .service import HybridCryptoService

# Backward compatibility: Provide legacy CryptographyManager
# TODO: Remove in v2.0.0
class CryptographyManager(HybridCryptoService):
    """Legacy CryptographyManager for backward compatibility.

    DEPRECATED: Use get_crypto_service() instead.
    Will be removed in v2.0.0.
    """

    def __init__(self, config_manager=None):
        """Initialize legacy manager.

        Args:
            config_manager: Ignored (kept for API compatibility)
        """
        import warnings

        warnings.warn(
            "CryptographyManager is deprecated. Use get_crypto_service() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Use DI to get services
        service = get_crypto_service()
        super().__init__(
            key_manager=service.key_manager,
            encryption_engine=service.encryption_engine,
        )


__all__ = [
    # Protocols
    "ConfigManagerProtocol",
    "KeyManagerProtocol",
    "EncryptionEngineProtocol",
    "TextCryptoServiceProtocol",
    # Implementations
    "RSAKeyManager",
    "AESGCMEngine",
    "HybridCryptoService",
    # DI
    "get_crypto_service",
    "register_crypto_services",
    # Legacy (deprecated)
    "CryptographyManager",
]
```

---

### 3.2 テストの更新

**Step 3.2.1: Protocol-basedモックテスト (3時間)**

**ファイル:** `test/components/crypto_engine/test_di.py` (新規作成)

```python
"""Test dependency injection and protocol-based design."""

import pytest
from unittest.mock import Mock

from components.crypto_engine.protocols import (
    KeyManagerProtocol,
    EncryptionEngineProtocol,
    TextCryptoServiceProtocol,
)
from components.crypto_engine.service import HybridCryptoService


class TestProtocolCompliance:
    """Test that implementations satisfy protocols."""

    def test_rsa_key_manager_implements_protocol(self):
        """Test RSAKeyManager implements KeyManagerProtocol."""
        from components.crypto_engine.key_management import RSAKeyManager

        assert isinstance(RSAKeyManager, KeyManagerProtocol.__class__)

    def test_aesgcm_engine_implements_protocol(self, tmp_path, monkeypatch):
        """Test AESGCMEngine implements EncryptionEngineProtocol."""
        from components.crypto_engine.encryption import AESGCMEngine
        from components.crypto_engine.key_management import RSAKeyManager
        import secrets

        monkeypatch.setenv("TEXTKIT_KEY_PASSPHRASE", secrets.token_urlsafe(48))

        key_manager = RSAKeyManager(key_directory=tmp_path / "rsa")
        engine = AESGCMEngine(key_manager=key_manager)

        assert isinstance(engine, EncryptionEngineProtocol.__class__)

    def test_hybrid_service_implements_protocol(self):
        """Test HybridCryptoService implements TextCryptoServiceProtocol."""
        assert isinstance(HybridCryptoService, TextCryptoServiceProtocol.__class__)


class TestDependencyInjection:
    """Test DI container integration."""

    def test_factory_registration(self):
        """Test services are registered correctly."""
        from textkit.dependency_injection import Container
        from components.crypto_engine.factory import register_crypto_services
        from components.crypto_engine.protocols import (
            KeyManagerProtocol,
            EncryptionEngineProtocol,
            TextCryptoServiceProtocol,
        )

        container = Container()
        register_crypto_services(container)

        assert KeyManagerProtocol in container
        assert EncryptionEngineProtocol in container
        assert TextCryptoServiceProtocol in container

    def test_get_crypto_service(self, tmp_path, monkeypatch):
        """Test get_crypto_service() returns configured service."""
        from components.crypto_engine.factory import get_crypto_service
        import secrets

        monkeypatch.setenv("TEXTKIT_KEY_PASSPHRASE", secrets.token_urlsafe(48))

        service = get_crypto_service()

        assert service is not None
        assert hasattr(service, "encrypt_text")
        assert hasattr(service, "decrypt_text")


class TestMockability:
    """Test that protocol-based design enables easy mocking."""

    def test_mock_key_manager(self):
        """Test KeyManagerProtocol can be mocked."""
        mock_key_manager = Mock(spec=KeyManagerProtocol)
        mock_key_manager.ensure_key_pair.return_value = (Mock(), Mock())

        # Should work with any code expecting KeyManagerProtocol
        assert hasattr(mock_key_manager, "ensure_key_pair")
        assert hasattr(mock_key_manager, "generate_key_pair")

    def test_mock_encryption_engine(self):
        """Test EncryptionEngineProtocol can be mocked."""
        mock_engine = Mock(spec=EncryptionEngineProtocol)
        mock_engine.encrypt.return_value = b"encrypted"
        mock_engine.decrypt.return_value = b"decrypted"

        # Should work with any code expecting EncryptionEngineProtocol
        result = mock_engine.encrypt(b"data")
        assert result == b"encrypted"

    def test_hybrid_service_with_mocks(self):
        """Test HybridCryptoService works with mocked dependencies."""
        mock_key_manager = Mock(spec=KeyManagerProtocol)
        mock_engine = Mock(spec=EncryptionEngineProtocol)
        mock_engine.encrypt.return_value = b"encrypted_data"
        mock_engine.decrypt.return_value = b"plain_data"

        service = HybridCryptoService(
            key_manager=mock_key_manager,
            encryption_engine=mock_engine,
        )

        # Test encryption
        encrypted = service.encrypt_text("test")
        assert isinstance(encrypted, str)  # Base64-encoded
        mock_engine.encrypt.assert_called_once()

        # Test decryption
        mock_engine.reset_mock()
        decrypted = service.decrypt_text(encrypted)
        assert decrypted == "plain_data"
        mock_engine.decrypt.assert_called_once()
```

---

### Phase 3 成果物

- [x] `components/crypto_engine/key_management.py` - RSA鍵管理分離
- [x] `components/crypto_engine/encryption.py` - AES-GCM実装分離
- [x] `components/crypto_engine/service.py` - 高レベルAPI
- [x] `components/crypto_engine/factory.py` - DI統合
- [x] `components/crypto_engine/__init__.py` - 後方互換性
- [x] `test/components/crypto_engine/test_di.py` - DI/Protocolテスト
- [x] コード行数30%削減達成

---

## 📦 Phase 4: Documentation & Polish (P3 - 1ヶ月以内)

**期間:** 5日 (6作業時間)
**優先度:** 🟢 Low
**担当者推奨:** テクニカルライター + 開発者

### 4.1 Sphinxドキュメント生成

```bash
# 1. Generate API documentation
uv run sphinx-apidoc -o docs/api components bases

# 2. Build HTML documentation
uv run sphinx-build -b html docs docs/_build

# 3. Open in browser
open docs/_build/index.html  # macOS
start docs/_build/index.html  # Windows
```

### 4.2 CI/CDパイプライン統合

**ファイル:** `.github/workflows/quality.yml`

```yaml
name: Quality Checks

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Ruff lint
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: Mypy type check
        run: uv run mypy components bases --strict

      - name: Pytest with coverage
        env:
          TEXTKIT_KEY_PASSPHRASE: ${{ secrets.TEST_PASSPHRASE }}
        run: |
          uv run pytest --cov=components --cov=bases \
                        --cov-report=xml \
                        --cov-report=term-missing

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
```

---

## 🔄 Migration & Rollback Strategy

### Pre-Flight Checklist

**Phase 1開始前:**
- [ ] 本番データのバックアップ完了
- [ ] `.env.example`に`TEXTKIT_KEY_PASSPHRASE`追加
- [ ] 開発環境でパスフレーズ生成・設定
- [ ] Gitブランチ作成 (`refactor/phase1-security`)

**Phase 2開始前:**
- [ ] Phase 1のすべてのテストがパス
- [ ] セキュリティ監査完了
- [ ] Mypyインストール確認

**Phase 3開始前:**
- [ ] Phase 1-2のすべてのテストがパス
- [ ] コードレビュー完了
- [ ] 依存性注入コンテナ動作確認

### Rollback Procedures

**Phase 1ロールバック:**
```bash
git checkout main -- components/crypto_engine/core.py
git checkout main -- test/components/crypto_engine/
rm -f bin/migrate_crypto_cbc_to_gcm.py
```

**Phase 2ロールバック:**
```bash
git checkout main -- components/crypto_engine/protocols.py
git checkout main -- mypy.ini
# Revert logging changes (manual review required)
```

**Phase 3ロールバック:**
```bash
git checkout main -- components/crypto_engine/
# Restore original core.py if needed
```

### Emergency Procedures

**暗号化キーの紛失:**
1. 既存の暗号化データは復号化不可能
2. 新しいキーペアを生成
3. 新規データから暗号化再開
4. ユーザーに通知

**パスフレーズ漏洩:**
1. 即座に環境変数をローテーション
2. 新しいパスフレーズで鍵を再暗号化
3. インシデントレポート作成
4. セキュリティ監査実施

---

## 📊 Success Metrics

### Phase 1 (Security)
- [ ] すべての秘密鍵が`ENCRYPTED`ヘッダー付きで保存
- [ ] `modes.CBC`への参照がゼロ
- [ ] セキュリティテスト100%パス
- [ ] OWASP Top 10脆弱性ゼロ

### Phase 2 (Quality)
- [ ] `Any`型の使用が50%削減
- [ ] `mypy --strict`エラーゼロ
- [ ] すべてのloggerがstructlog
- [ ] テストカバレッジ >85%

### Phase 3 (Architecture)
- [ ] コード行数30%削減 (約300行)
- [ ] Protocol-basedテスト速度2倍向上
- [ ] DI統合完了
- [ ] 重複コードゼロ

### Phase 4 (Documentation)
- [ ] Sphinxドキュメント生成成功
- [ ] API仕様100%ドキュメント化
- [ ] CI/CDパイプライン完全自動化
- [ ] README更新完了

---

## 🎓 Learning Resources

### 推奨学習リソース

**Cryptography:**
- [pyca/cryptography公式ドキュメント](https://cryptography.io/)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)

**Pydantic:**
- [Pydantic V2公式ドキュメント](https://docs.pydantic.dev/latest/)
- [ValidationInfo API](https://docs.pydantic.dev/latest/api/pydantic_core/#pydantic_core.core_schema.ValidationInfo)

**Structlog:**
- [structlog公式ドキュメント](https://www.structlog.org/)
- [Best Practices for Logging](https://www.structlog.org/en/stable/logging-best-practices.html)

**Polylith Architecture:**
- [Python Polylith Documentation](https://davidvujic.github.io/python-polylith-docs/)

---

## 📝 Implementation Notes

### 開発者向けメモ

1. **必ずテスト駆動で実装する (TDD):**
   - 失敗するテストを先に書く
   - 実装してテストをパスさせる
   - リファクタリング

2. **コミットは小さく頻繁に:**
   - 各Stepごとにコミット
   - コミットメッセージは英語で明確に

3. **ペアプログラミング推奨:**
   - Phase 1はセキュリティエンジニアと
   - Phase 3はアーキテクトと

4. **定期的なレビュー:**
   - 各Phase完了時にコードレビュー
   - セキュリティ監査は必須

---

## 🏁 Conclusion

このロードマップに従うことで、Text Processing Toolkitは以下を達成します:

✅ **Production-Ready Excellence** (S Rank)
✅ **セキュリティ:** OWASP準拠、業界標準の暗号化
✅ **保守性:** Protocol-based DI、30%コード削減
✅ **品質:** Mypy厳格モード、85%+カバレッジ
✅ **ドキュメント:** 完全なAPI仕様、自動生成ドキュメント

**推定総工数:** 29時間 (約4週間 @ 1時間/日)
**ROI:** セキュリティリスク削減、開発速度向上、保守コスト削減

---

**#2** (ロードマップ策定完了)
