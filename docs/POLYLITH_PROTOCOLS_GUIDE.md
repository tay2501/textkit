# Polylith Protocol-Oriented Design Guide

**作成日:** 2025-12-11
**ステータス:** Best Practices Implementation

---

## 📋 概要

このガイドは、TextKitプロジェクトにおけるProtocol-Oriented Design（プロトコル指向設計）のベストプラクティスを定義します。

---

## 🎯 プロトコル指向設計の原則

### 1. **Protocolの定義**

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class TransformerProtocol(Protocol):
    """Text transformer protocol for loose coupling."""

    def transform(self, text: str) -> str:
        """Transform input text.

        Args:
            text: Input text to transform

        Returns:
            Transformed text
        """
        ...

    @property
    def name(self) -> str:
        """Transformer name for identification."""
        ...
```

### 2. **Protocol実装（暗黙的）**

```python
# Protocolを明示的に継承する必要はない
class UpperCaseTransformer:
    """Uppercase transformer implementing TransformerProtocol."""

    def transform(self, text: str) -> str:
        return text.upper()

    @property
    def name(self) -> str:
        return "uppercase"

# 実行時チェック
transformer = UpperCaseTransformer()
assert isinstance(transformer, TransformerProtocol)  # True
```

### 3. **依存性注入との統合**

```python
from lagom import Container

container = Container()
container[TransformerProtocol] = UpperCaseTransformer

# 使用時
def process_text(text: str, transformer: TransformerProtocol) -> str:
    return transformer.transform(text)
```

---

## 📦 既存のProtocol実装

### `components/text_core/types.py`

```python
# 設定マネージャープロトコル
@runtime_checkable
class ConfigManagerProtocol(Protocol):
    def get_config(self, key: str) -> Any: ...
    def set_config(self, key: str, value: Any) -> None: ...

# トランスフォーマープロトコル
@runtime_checkable
class TransformerProtocol(Protocol):
    def transform(self, text: str) -> str: ...

# I/Oマネージャープロトコル
@runtime_checkable
class IOManagerProtocol(Protocol):
    def get_input_text(self) -> str: ...
    def set_output_text(self, text: str) -> None: ...

# 暗号化マネージャープロトコル
@runtime_checkable
class CryptoManagerProtocol(Protocol):
    def encrypt(self, plaintext: str) -> str: ...
    def decrypt(self, ciphertext: str) -> str: ...
```

---

## 🔧 推奨パターン

### パターン1: Strategy Pattern with Protocols

```python
from typing import Protocol

class ValidationStrategy(Protocol):
    def validate(self, data: Any) -> bool: ...

class EmailValidator:
    def validate(self, data: str) -> bool:
        return "@" in data and "." in data.split("@")[1]

class PhoneValidator:
    def validate(self, data: str) -> bool:
        return data.replace("-", "").isdigit()

def validate_input(data: str, strategy: ValidationStrategy) -> bool:
    return strategy.validate(data)
```

### パターン2: Factory Pattern with Protocols

```python
from typing import Protocol

class Serializer(Protocol):
    def serialize(self, data: dict) -> str: ...
    def deserialize(self, data: str) -> dict: ...

class JSONSerializer:
    def serialize(self, data: dict) -> str:
        import json
        return json.dumps(data)

    def deserialize(self, data: str) -> dict:
        import json
        return json.loads(data)

def create_serializer(format_type: str) -> Serializer:
    if format_type == "json":
        return JSONSerializer()
    # ... other formats
```

### パターン3: Observer Pattern with Protocols

```python
from typing import Protocol

class Observer(Protocol):
    def update(self, event: str, data: Any) -> None: ...

class LoggingObserver:
    def update(self, event: str, data: Any) -> None:
        logger.info(f"Event: {event}, Data: {data}")

class MetricsObserver:
    def update(self, event: str, data: Any) -> None:
        metrics.record(event, data)

class Subject:
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def notify(self, event: str, data: Any) -> None:
        for observer in self._observers:
            observer.update(event, data)
```

---

## ✅ ベストプラクティス

### 1. **@runtime_checkableの使用**

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Processor(Protocol):
    def process(self, data: str) -> str: ...

# 実行時チェックが可能
def safe_process(processor: Any, data: str) -> str:
    if not isinstance(processor, Processor):
        raise TypeError(f"{processor} does not implement Processor")
    return processor.process(data)
```

### 2. **Generic Protocolsの活用**

```python
from typing import Protocol, TypeVar, Generic

T = TypeVar('T')
R = TypeVar('R')

class Transformer(Protocol, Generic[T, R]):
    def transform(self, input: T) -> R: ...

# 具体的な型での使用
class StringToIntTransformer:
    def transform(self, input: str) -> int:
        return len(input)

transformer: Transformer[str, int] = StringToIntTransformer()
```

### 3. **Protocol Compositionの推奨**

```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...

class Writable(Protocol):
    def write(self, data: str) -> None: ...

class ReadWritable(Readable, Writable, Protocol):
    """Combined read-write protocol."""
    pass
```

---

## 🚫 アンチパターン

### ❌ 避けるべきパターン1: Abstract Base Classes (ABC)の過度な使用

```python
# ❌ 避ける
from abc import ABC, abstractmethod

class Transformer(ABC):
    @abstractmethod
    def transform(self, text: str) -> str:
        pass

# ✅ 推奨
from typing import Protocol

class Transformer(Protocol):
    def transform(self, text: str) -> str: ...
```

**理由:** Protocolは構造的部分型（structural subtyping）により、既存コードの変更なしで適用可能。

### ❌ 避けるべきパターン2: 過度に大きなProtocol

```python
# ❌ 避ける: God Object Pattern
class DataProcessor(Protocol):
    def read(self) -> str: ...
    def write(self, data: str) -> None: ...
    def validate(self, data: str) -> bool: ...
    def transform(self, data: str) -> str: ...
    def encrypt(self, data: str) -> str: ...
    def compress(self, data: str) -> bytes: ...

# ✅ 推奨: 単一責任原則に従う
class Reader(Protocol):
    def read(self) -> str: ...

class Writer(Protocol):
    def write(self, data: str) -> None: ...

class Validator(Protocol):
    def validate(self, data: str) -> bool: ...
```

---

## 📊 Polylithアーキテクチャとの統合

### コンポーネント間の疎結合

```
components/
├── text_core/
│   ├── types.py          # Protocols定義
│   └── core.py           # Protocol使用
├── crypto_engine/
│   ├── protocols.py      # Crypto-specific protocols
│   └── core.py           # Implementation
└── io_handler/
    ├── types.py          # I/O protocols
    └── core.py           # Implementation
```

### 依存関係の方向

```
Base ← Component (Protocol定義)
  ↑
Implementation (Protocol実装)
```

---

## 🔍 チェックリスト

新しいProtocolを追加する際のチェックリスト：

- [ ] `@runtime_checkable`デコレータを追加
- [ ] メソッドシグネチャに型ヒントを完備
- [ ] Docstringで各メソッドの責務を明確化
- [ ] 単一責任原則に従う（1つの目的）
- [ ] 既存のProtocolとの重複がないか確認
- [ ] Mypyでの型チェック通過を確認

---

## 📚 参考資料

- [PEP 544 – Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Python Typing Documentation](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Polylith Architecture](https://davidvujic.github.io/python-polylith-docs/)
