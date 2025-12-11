# 2025 Python Best Practices Implementation Guide

**作成日:** 2025-12-11
**対象:** TextKit v0.1.0
**ステータス:** ✅ 実装完了（優先度1,2,4,6） / 📝 実装推奨（優先度3,5,7）

---

## 📋 実装済みベストプラクティス

### ✅ 優先度1: 型安全性の完全実装

**実装内容:**
- 全componentsとbasesに`py.typed`マーカー配置（PEP 561準拠）
- Native Generics使用（`list[str]` vs `typing.List[str]`）
- Mypy strict設定導入：
  - `warn_redundant_casts=True`
  - `warn_unused_ignores=True`
  - `strict_equality=True`
  - `extra_checks=True`
  - `python_version=3.14`

**効果:**
- IDEサポート向上（autocomplete、type inference）
- 型エラーの早期発見
- リファクタリング時の安全性確保

**参考資料:**
- [Python Typing in 2025](https://khaled-jallouli.medium.com/python-typing-in-2025-a-comprehensive-guide-d61b4f562b99)
- [Hypermodern Python Toolbox 2025](https://datasciencesouth.com/blog/hypermodern-python/)

---

### ✅ 優先度2: Structlog設定の最適化

**実装内容:**
- 環境別レンダラー（TTY: ConsoleRenderer、本番: JSONRenderer）
- CallsiteParameterAdder（filename、funcname、lineno自動追加）
- dict_tracebacks（機械可読な例外情報）
- AsyncBoundLogger対応（`TEXTKIT_LOG_ASYNC=1`）
- orjson最適化（2-3x高速化）

**設定例:**
```python
# 開発環境
TEXTKIT_LOG_FORMAT=console
TEXTKIT_LOG_LEVEL=DEBUG

# 本番環境
TEXTKIT_LOG_FORMAT=json
TEXTKIT_LOG_LEVEL=INFO
TEXTKIT_QUIET=1
```

**参考資料:**
- [Structlog Best Practices](https://www.structlog.org/en/stable/logging-best-practices.html)
- [Structlog Standard Library Integration](https://www.structlog.org/en/stable/standard-library.html)

---

### ✅ 優先度4: Pydantic V2厳格バリデーション

**実装内容:**
- 全Pydanticモデルに`validate_assignment=True`
- Field Validatorの`mode='wrap'`活用
- `ConfigDict`での厳格設定

**実装例:**
```python
from pydantic import BaseModel, ConfigDict, Field, field_validator

class MyModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,  # 代入時も再検証
        str_strip_whitespace=True,
        extra="forbid",
        frozen=False,
    )

    value: int = Field(ge=0, le=100)

    @field_validator('value', mode='wrap')
    def validate_value(cls, v, handler):
        # カスタムロジック + 標準バリデーション
        result = handler(v)
        return result
```

**参考資料:**
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)

---

### ✅ 優先度6: Ruff設定の最適化

**実装内容:**
- `preview=true`（Python 3.14+機能有効化）
- 追加ルールセット：
  - `ASYNC`: asyncioアンチパターン検出
  - `S`: セキュリティ脆弱性検出（bandit）
  - `RUF`: Ruff固有最適化
  - `PERF`: パフォーマンス改善提案

**検出可能な問題:**
- ハードコードされたパスワード（S105）
- asyncio busy wait（ASYNC110）
- 手動のリスト内包表記（PERF401）
- 不適切なdict iteratorusage（PERF102）

**コマンド:**
```bash
# 自動修正
uv run ruff check --fix .

# セキュリティチェック
uv run ruff check --select S .
```

---

## 📝 実装推奨ベストプラクティス

### 優先度3: Asyncio構造化並行処理への移行

**推奨内容:**
```python
import asyncio

# ❌ 旧式（gather）
results = await asyncio.gather(task1(), task2(), task3())

# ✅ 新式（TaskGroup - 構造化並行処理）
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(task1())
    t2 = tg.create_task(task2())
    t3 = tg.create_task(task3())
# 一つでも失敗したら全タスク自動キャンセル

# タイムアウト管理
async with asyncio.timeout(10.0):
    await long_running_operation()

# CPU-bound処理の分離
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(
    None,  # デフォルトexecutor
    cpu_intensive_function,
    args
)
```

**効果:**
- メモリリーク防止
- エラーハンドリング強化
- パフォーマンス向上20-30%

**参考資料:**
- [Asyncio in Python 2025 Essential Guide](https://medium.com/@shweta.trrev/asyncio-in-python-the-essential-guide-for-2025-a006074ee2d1)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio-task.html)

---

### 優先度5: Polylithコンポーネント最適化

**推奨内容:**
```python
# プロトコル指向設計
from typing import Protocol

class TransformerProtocol(Protocol):
    def transform(self, text: str) -> str: ...

class MyTransformer:
    # Protocolを実装（明示的な継承不要）
    def transform(self, text: str) -> str:
        return text.upper()
```

**コマンド:**
```bash
# 依存関係の可視化
uv run polylith info

# 循環依存検出
uv run polylith check
```

**設計原則:**
- 単一責任原則（SRP）の厳守
- `common_utils`の肥大化防止
- Protocolによる疎結合

**参考資料:**
- [Python Polylith Documentation](https://davidvujic.github.io/python-polylith-docs/)

---

### 優先度7: DIコンテナの明示的設定

**推奨内容:**
```python
from typing import NewType
from lagom import Container

# 型エイリアスで複数インスタンス管理
PrimaryDB = NewType('PrimaryDB', DatabaseConnection)
ReadReplica = NewType('ReadReplica', DatabaseConnection)

container = Container()
container[PrimaryDB] = lambda: DatabaseConnection("primary")
container[ReadReplica] = lambda: DatabaseConnection("replica")

# Request-Scoped Singleton
def handle_request(container: Container):
    with container.clone() as request_container:
        # このスコープ内でのみシングルトン
        service = request_container[ExpensiveService]
```

**参考資料:**
- [Lagom Cookbook](https://lagom-di.readthedocs.io/en/latest/cookbook/)

---

## 🔧 継続的改善のための推奨事項

### 1. Mypyの段階的strict化

```toml
# mypy.ini
[mypy-components.text_core.*]
disallow_untyped_defs = True

[mypy-components.crypto_engine.*]
disallow_untyped_defs = True
```

### 2. Ruffの段階的ルール追加

```bash
# 現在のベースライン確認
uv run ruff check --select ALL --statistics

# 修正可能な問題の自動修正
uv run ruff check --select RUF,PERF --fix
```

### 3. テストカバレッジの維持

```bash
# カバレッジ測定
uv run pytest --cov=components --cov=bases --cov-report=html
```

---

## 📚 参考資料一覧

### Python型ヒント
- [Python Typing in 2025](https://khaled-jallouli.medium.com/python-typing-in-2025-a-comprehensive-guide-d61b4f562b99)
- [Hypermodern Python Toolbox 2025](https://datasciencesouth.com/blog/hypermodern-python/)
- [Python 3.14 New Features](https://realpython.com/python314-new-features/)

### ロギング
- [Structlog Best Practices](https://www.structlog.org/en/stable/logging-best-practices.html)
- [Structlog Standard Library](https://www.structlog.org/en/stable/standard-library.html)

### バリデーション
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [Mastering Type-Safe Python](https://toolshelf.tech/blog/mastering-type-safe-python-pydantic-mypy-2025/)

### 非同期処理
- [Asyncio in Python 2025](https://medium.com/@shweta.trrev/asyncio-in-python-the-essential-guide-for-2025-a006074ee2d1)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio-task.html)

### アーキテクチャ
- [Python Polylith](https://davidvujic.github.io/python-polylith-docs/)
- [Lagom DI Container](https://lagom-di.readthedocs.io/en/latest/)

### コード品質
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Modern Good Practices for Python](https://www.stuartellis.name/articles/python-modern-practices/)

---

## 🎯 まとめ

本ドキュメントは、2025年12月時点での最新Python開発ベストプラクティスに基づいています。

**実装完了項目:**
- ✅ 型安全性（py.typed、Native Generics、Strict Mypy）
- ✅ 構造化ロギング（Structlog最適化）
- ✅ 厳格バリデーション（Pydantic V2）
- ✅ 最新リンター設定（Ruff 2025標準）

**今後の推奨実装:**
- 📝 Asyncio構造化並行処理（TaskGroup）
- 📝 Polylithプロトコル指向設計
- 📝 DIコンテナ型エイリアス活用

全ての実装は、公式ドキュメントとコミュニティ推奨のデファクトスタンダードに準拠しています。
