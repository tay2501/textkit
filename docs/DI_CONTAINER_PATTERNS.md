# Dependency Injection Container Patterns with Lagom

**作成日:** 2025-12-11
**ステータス:** Best Practices Guide

---

## 📋 概要

このガイドは、TextKitプロジェクトにおけるLagom DIコンテナの推奨パターンと実装方法を定義します。

---

## 🎯 基本パターン

### 1. **型ベース自動配線（Type-Based Autowiring）**

```python
from lagom import Container

container = Container()

class DatabaseConnection:
    def __init__(self, host: str = "localhost"):
        self.host = host

class UserRepository:
    def __init__(self, db: DatabaseConnection):  # 自動注入
        self.db = db

# 自動配線（型ヒントに基づく）
repo = container[UserRepository]
```

### 2. **明示的な設定（Explicit Configuration）**

```python
from lagom import Container

container = Container()

# Lambda関数での明示的設定
container[DatabaseConnection] = lambda: DatabaseConnection(host="prod-db")

# ファクトリ関数
def create_repository() -> UserRepository:
    db = DatabaseConnection(host="prod-db")
    return UserRepository(db)

container[UserRepository] = create_repository
```

---

## 🔧 高度なパターン

### パターン1: 型エイリアスで複数インスタンス管理

```python
from typing import NewType
from lagom import Container

# 型エイリアスの定義
PrimaryDB = NewType('PrimaryDB', DatabaseConnection)
ReadReplica = NewType('ReadReplica', DatabaseConnection)
AnalyticsDB = NewType('AnalyticsDB', DatabaseConnection)

container = Container()

# 各インスタンスの設定
container[PrimaryDB] = lambda: DatabaseConnection("primary.db")
container[ReadReplica] = lambda: DatabaseConnection("replica.db")
container[AnalyticsDB] = lambda: DatabaseConnection("analytics.db")

# 使用例
class DataService:
    def __init__(
        self,
        primary: PrimaryDB,
        replica: ReadReplica,
    ):
        self.primary = primary
        self.replica = replica

    def write(self, data: str) -> None:
        # Primaryに書き込み
        pass

    def read(self) -> str:
        # Read Replicaから読み込み
        pass
```

### パターン2: Request-Scoped Singleton

```python
from lagom import Container
import uuid

def handle_request(request_id: str | None = None):
    """Handle a single request with request-scoped dependencies."""
    # グローバルコンテナのクローン作成
    global_container = Container()

    with global_container.clone() as request_container:
        # このスコープ内でのみシングルトン
        request_id = request_id or str(uuid.uuid4())

        # Request-scoped services
        request_container[RequestContext] = lambda: RequestContext(request_id)

        # サービス取得（同一リクエスト内で同じインスタンス）
        service1 = request_container[ExpensiveService]
        service2 = request_container[ExpensiveService]

        assert service1 is service2  # 同一インスタンス

    # スコープ外では新しいインスタンス
```

### パターン3: Injectable Markerパターン

```python
from lagom import injectable, Container

class UserService:
    def __init__(
        self,
        db: DatabaseConnection,
        cache_ttl: int = injectable,  # Lagomが注入
        max_retries: int = 3,  # デフォルト値（注入されない）
    ):
        self.db = db
        self.cache_ttl = cache_ttl
        self.max_retries = max_retries

container = Container()
container[int] = lambda: 3600  # cache_ttl用

service = container[UserService]
# service.cache_ttl == 3600 (注入された)
# service.max_retries == 3 (デフォルト値)
```

### パターン4: Shared Dependencies（共有依存関係）

```python
from lagom import Container

class ExpensiveResource:
    """コスト高なリソース（DB接続、API client等）."""

    def __init__(self):
        print("Initializing expensive resource...")

def process_requests_with_shared_resource():
    """複数のサービスで同じリソースを共有."""
    container = Container()

    # Shared dependency登録
    def get_shared_services():
        return container.partial(ExpensiveResource)

    container[ExpensiveResource] = get_shared_services

    # 同じ関数呼び出し内で同じインスタンス
    service1 = container[ServiceA]  # ExpensiveResourceを使用
    service2 = container[ServiceB]  # 同じExpensiveResourceを使用
```

---

## 📦 TextKitでの実装例

### 既存のDIコンテナ設定

```python
# components/dependency_injection/__init__.py

from lagom import Container, Singleton, injectable

# Global container instance
_container: Container | None = None

def get_container() -> Container:
    """Get or create the global container instance."""
    global _container
    if _container is None:
        _container = Container(log_undefined_deps=True)
    return _container

def get_service(service_type):
    """Get a service from the global container."""
    container = get_container()
    return container[service_type]
```

### 推奨: 型エイリアスの追加

```python
# components/dependency_injection/types.py

from typing import NewType
from components.config_manager.settings import ApplicationSettings
from components.text_core.core import TextTransformationEngine

# 環境別設定
DevelopmentSettings = NewType('DevelopmentSettings', ApplicationSettings)
ProductionSettings = NewType('ProductionSettings', ApplicationSettings)

# エンジン別インスタンス
PrimaryEngine = NewType('PrimaryEngine', TextTransformationEngine)
BackupEngine = NewType('BackupEngine', TextTransformationEngine)

# セットアップ
def setup_container(container: Container, env: str = "development"):
    """Setup container with environment-specific dependencies."""
    if env == "development":
        container[DevelopmentSettings] = lambda: ApplicationSettings(
            debug_mode=True,
            log_level="DEBUG"
        )
    else:
        container[ProductionSettings] = lambda: ApplicationSettings(
            debug_mode=False,
            log_level="INFO"
        )

    # エンジン設定
    container[PrimaryEngine] = lambda: TextTransformationEngine()
    container[BackupEngine] = lambda: TextTransformationEngine()
```

---

## ✅ ベストプラクティス

### 1. **log_undefined_deps=Trueの使用**

```python
# 未定義の依存関係を早期検出
container = Container(log_undefined_deps=True)
```

### 2. **型アノテーションの徹底**

```python
# ❌ 避ける
def create_service():
    return UserService(...)

# ✅ 推奨
def create_service() -> UserService:
    return UserService(...)

container[UserService] = create_service
```

### 3. **循環依存の回避**

```python
# ❌ 避ける: 循環依存
class ServiceA:
    def __init__(self, b: ServiceB): ...

class ServiceB:
    def __init__(self, a: ServiceA): ...

# ✅ 推奨: イベントベースまたはProtocol使用
from typing import Protocol

class ServiceBProtocol(Protocol):
    def do_something(self) -> None: ...

class ServiceA:
    def __init__(self, b: ServiceBProtocol): ...
```

### 4. **テストでのコンテナオーバーライド**

```python
import pytest
from lagom import Container

@pytest.fixture
def test_container():
    """Test用のコンテナ."""
    container = Container()

    # モックで置き換え
    container[DatabaseConnection] = lambda: MockDatabase()

    return container

def test_user_service(test_container):
    service = test_container[UserService]
    assert isinstance(service.db, MockDatabase)
```

---

## 🚫 アンチパターン

### ❌ 避けるべきパターン1: Service Locator Pattern

```python
# ❌ 避ける: Service Locatorパターン
class UserService:
    def __init__(self):
        # コンストラクタ内でコンテナを直接使用
        self.db = get_container()[DatabaseConnection]

# ✅ 推奨: Constructor Injection
class UserService:
    def __init__(self, db: DatabaseConnection):
        self.db = db
```

### ❌ 避けるべきパターン2: マジックストリング使用

```python
# ❌ 避ける: 文字列ベースの依存関係
container["database"] = lambda: DatabaseConnection()
db = container["database"]

# ✅ 推奨: 型ベースの依存関係
container[DatabaseConnection] = lambda: DatabaseConnection()
db = container[DatabaseConnection]
```

---

## 📊 パフォーマンス考慮事項

### 1. **Lazy Initialization（遅延初期化）**

```python
# Lambda関数で遅延初期化
container[ExpensiveResource] = lambda: ExpensiveResource()

# 最初のアクセス時に初期化
resource = container[ExpensiveResource]
```

### 2. **Singleton Pattern（シングルトン）**

```python
from lagom import Singleton

# Singletonデコレータ
@Singleton
class ConfigurationManager:
    def __init__(self):
        self.config = load_config()

container[ConfigurationManager] = ConfigurationManager
```

---

## 🔍 デバッグとトラブルシューティング

### 依存関係の可視化

```python
import inspect

def debug_container(container: Container, service_type: type):
    """コンテナの依存関係をデバッグ."""
    print(f"Resolving {service_type.__name__}:")

    sig = inspect.signature(service_type.__init__)
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue

        param_type = param.annotation
        print(f"  - {param_name}: {param_type}")

        if param_type in container._dependencies:
            print(f"    ✓ Registered")
        else:
            print(f"    ✗ Not registered (will auto-wire)")
```

### エラーハンドリング

```python
from components.dependency_injection import get_container
from components.exceptions import DependencyResolutionError

def safe_get_service(service_type: type):
    """安全なサービス取得（エラーハンドリング付き）."""
    try:
        container = get_container()
        return container[service_type]
    except Exception as e:
        raise DependencyResolutionError(
            f"Failed to resolve {service_type.__name__}: {e}"
        )
```

---

## 📚 参考資料

- [Lagom Documentation](https://lagom-di.readthedocs.io/en/latest/)
- [Lagom Cookbook](https://lagom-di.readthedocs.io/en/latest/cookbook/)
- [Dependency Injection in Python](https://python-dependency-injector.ets-labs.org/)

---

## 🎯 まとめ

Lagom DIコンテナのベストプラクティス：

1. **型エイリアス**で複数インスタンス管理
2. **Request-Scoped**でリクエスト単位のシングルトン
3. **Injectable Marker**で明示的な注入制御
4. **Shared Dependencies**でリソース効率化
5. **型アノテーション**の徹底
6. **循環依存**の回避

これらのパターンにより、保守性・テスタビリティ・パフォーマンスの高いアプリケーションを実現できます。
