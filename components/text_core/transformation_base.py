"""
抽象基底クラスとチE��スト変換プロトコルの定義

こ�Eモジュールは、すべてのチE��スト変換クラスが継承すべき抽象基底クラスと
型安�E性を保証するプロトコルを提供します、E"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

from .exceptions import ValidationError, TransformationError
from .types import ConfigDict, ErrorContext








class TransformationBase(ABC):
    """すべてのチE��スト変換クラスの抽象基底クラス

    こ�Eクラスは変換処琁E�E共通インターフェースを定義し、E    実裁E��ラスが忁E��メソチE��を持つことを保証します、E    """

    def __init__(self, config: ConfigDict | None = None) -> None:
        """抽象基底クラスの初期匁E
        Args:
            config: 変換設定辞書�E�オプション�E�E        """
        self._config: ConfigDict = config or {}
        self._is_initialized: bool = False
        self._error_context: ErrorContext = {}

    @abstractmethod
    def transform(self, text: str) -> str:
        """チE��スト変換を実行する抽象メソチE��

        Args:
            text: 変換対象のチE��スチE
        Returns:
            変換されたテキスチE
        Raises:
            TransformationError: 変換処琁E��失敗した場吁E        """
        ...

    @abstractmethod
    def get_transformation_rule(self) -> str:
        """適用される変換ルールを取得する抽象メソチE��

        Returns:
            変換ルール斁E���E�E�侁E '/t', '/l', '/u'など�E�E        """
        ...

    @abstractmethod
    def get_input_text(self) -> str:
        """変換前�E斁E���Eを取得する抽象メソチE��

        Returns:
            変換前�E斁E���E
        """
        ...

    @abstractmethod
    def get_output_text(self) -> str:
        """変換後�E斁E���Eを取得する抽象メソチE��

        Returns:
            変換後�E斁E���E
        """
        ...

    def validate_input(self, text: str) -> bool:
        """入力テキスト�E妥当性を検証

        Args:
            text: 検証対象のチE��スチE
        Returns:
            入力が妥当な場吁Erue
        """
        try:
            return isinstance(text, str)
        except Exception:
            # EAFPスタイル: 例外が発生した場合�E無効とみなぁE            return False

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """設定値を取征E
        Args:
            key: 設定キー
            default: チE��ォルト値

        Returns:
            設定値また�EチE��ォルト値
        """
        try:
            return self._config[key]
        except KeyError:
            # EAFPスタイル: キーが存在しなぁE��合�EチE��ォルトを返す
            return default

    def set_error_context(self, context: ErrorContext) -> None:
        """エラーコンチE��ストを設宁E
        Args:
            context: エラー惁E��を含む辞書
        """
        import contextlib

        with contextlib.suppress(Exception):
            # EAFPスタイル: 更新に失敗した場合�E無要E            self._error_context.update(context)

    def get_error_context(self) -> ErrorContext:
        """現在のエラーコンチE��ストを取征E
        Returns:
            エラーコンチE��スト辞書
        """
        try:
            return self._error_context.copy()
        except Exception:
            # EAFPスタイル: コピ�Eに失敗した場合�E空辞書を返す
            return {}

    def set_arguments(self, args: list[str]) -> None:
        """変換処琁E�E引数を設定（オプションメソチE���E�E
        Args:
            args: 変換処琁E��渡す引数のリスチE
        Note:
            こ�EメソチE��は引数を忁E��とする変換クラスでオーバ�Eライドされる
            基本実裁E��は何も行わなぁE���E示皁E��no-op�E�E        """
        # Explicit no-op: This is an optional hook method
        # Subclasses that need arguments will override this method

    def _safe_transform(self, text: str) -> str:
        """安�Eな変換実行�Eヘルパ�EメソチE��

        Args:
            text: 変換対象のチE��スチE
        Returns:
            変換されたテキスチE
        Raises:
            ValidationError: 入力検証に失敗した場吁E            TransformationError: 変換処琁E��失敗した場吁E        """
        # EAFPスタイル: まず変換を試行し、失敗時に詳細検証
        try:
            if not self.validate_input(text):
                raise ValidationError(
                    f"入力検証に失敁E {type(text).__name__}",
                    {"input_type": type(text).__name__, "input_value": str(text)[:100]},
                )

            return self.transform(text)

        except ValidationError:
            raise
        except Exception as e:
            # 変換失敗時のエラーコンチE��ストを設宁E            self.set_error_context(
                {
                    "transform_error": str(e),
                    "error_type": type(e).__name__,
                    "input_length": len(text) if isinstance(text, str) else 0,
                }
            )
            raise TransformationError(f"変換処琁E��失敁E {e}", self.get_error_context()) from e


@runtime_checkable
class TextTransformerProtocol(Protocol):
    """チE��スト変換処琁E�Eプロトコル定義

    こ�Eプロトコルは変換クラスが実裁E��べきメソチE��を定義し、E    型安�E性を保証します、E    """

    def transform(self, text: str) -> str:
        """チE��スト変換を実衁E
        Args:
            text: 変換対象のチE��スチE
        Returns:
            変換されたテキスチE        """
        ...

    def validate_input(self, text: str) -> bool:
        """入力テキスト�E妥当性を検証

        Args:
            text: 検証対象のチE��スチE
        Returns:
            入力が妥当な場吁Erue
        """
        ...

    def get_transformation_rule(self) -> str:
        """適用される変換ルールを取征E
        Returns:
            変換ルール斁E���E�E�侁E '/t', '/l', '/u'など�E�E        """
        ...

    def get_input_text(self) -> str:
        """変換前�E斁E���Eを取征E
        Returns:
            変換前�E斁E���E
        """
        ...

    def get_output_text(self) -> str:
        """変換後�E斁E���Eを取征E
        Returns:
            変換後�E斁E���E
        """
        ...


@runtime_checkable
class ConfigurableTransformerProtocol(TextTransformerProtocol, Protocol):
    """設定可能な変換処琁E�Eプロトコル定義

    こ�Eプロトコルは設定を持つ変換クラスが実裁E��べぁE    メソチE��を定義します、E    """

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """設定値を取征E
        Args:
            key: 設定キー
            default: チE��ォルト値

        Returns:
            設定値また�EチE��ォルト値
        """
        ...

    def set_error_context(self, context: ErrorContext) -> None:
        """エラーコンチE��ストを設宁E
        Args:
            context: エラー惁E��を含む辞書
        """
        ...


class ChainableTransformationBase(TransformationBase):
    """チェイン可能な変換処琁E�E抽象基底クラス

    褁E��の変換を連鎖して実行できる機�Eを提供します、E    """

    def __init__(self, config: ConfigDict | None = None) -> None:
        """チェイン可能変換クラスの初期匁E
        Args:
            config: 変換設定辞書�E�オプション�E�E        """
        super().__init__(config)
        self._chain: list[TransformationBase] = []

    def add_transformer(self, transformer: TransformationBase) -> None:
        """変換処琁E��チェインに追加

        Args:
            transformer: 追加する変換処琁E        """
        try:
            if not isinstance(transformer, TransformationBase):
                raise ValidationError(
                    f"変換処琁E�E TransformationBase を継承する忁E��がありまぁE {type(transformer).__name__}"
                )
            self._chain.append(transformer)
        except Exception as e:
            # EAFPスタイル: 追加に失敗した場合�Eエラーを記録
            self.set_error_context(
                {
                    "chain_add_error": str(e),
                    "transformer_type": type(transformer).__name__,
                }
            )
            raise

    def chain_transform(self, text: str) -> str:
        """チェインされた変換を頁E��実衁E
        Args:
            text: 変換対象のチE��スチE
        Returns:
            チェイン変換されたテキスチE
        Raises:
            TransformationError: チェイン変換に失敗した場吁E        """
        try:
            result: str = text

            for i, transformer in enumerate(self._chain):
                try:
                    result = transformer._safe_transform(result)
                except Exception as e:
                    # チェイン冁E�E変換失敗時のコンチE��スチE                    self.set_error_context(
                        {
                            "chain_position": i,
                            "transformer_type": type(transformer).__name__,
                            "chain_error": str(e),
                        }
                    )
                    raise TransformationError(
                        f"チェイン変換の第{i+1}段階で失敁E {e}",
                        self.get_error_context(),
                    ) from e

            return result

        except TransformationError:
            raise
        except Exception as e:
            raise TransformationError(
                f"チェイン変換処琁E��失敁E {e}", self.get_error_context()
            ) from e

    def clear_chain(self) -> None:
        """変換チェインをクリア"""
        import contextlib

        with contextlib.suppress(Exception):
            # EAFPスタイル: クリアに失敗した場合�E無要E            self._chain.clear()

    def get_chain_length(self) -> int:
        """チェインの長さを取征E
        Returns:
            チェインに含まれる変換処琁E�E数
        """
        try:
            return len(self._chain)
        except Exception:
            # EAFPスタイル: 長さ取得に失敗した場合�E0を返す
            return 0


def is_text_transformer(obj: Any) -> bool:
    """オブジェクトが TextTransformerProtocol を実裁E��てぁE��か検証

    Args:
        obj: 検証対象のオブジェクチE
    Returns:
        プロトコルを実裁E��てぁE��場吁Erue
    """
    try:
        return isinstance(obj, TextTransformerProtocol)
    except Exception:
        # EAFPスタイル: 検証に失敗した場合�EFalseを返す
        return False


def is_configurable_transformer(obj: Any) -> bool:
    """オブジェクトが ConfigurableTransformerProtocol を実裁E��てぁE��か検証

    Args:
        obj: 検証対象のオブジェクチE
    Returns:
        プロトコルを実裁E��てぁE��場吁Erue
    """
    try:
        return isinstance(obj, ConfigurableTransformerProtocol)
    except Exception:
        # EAFPスタイル: 検証に失敗した場合�EFalseを返す
        return False


def create_safe_transformer(
    transformer_class: type[TransformationBase], config: ConfigDict | None = None
) -> TransformationBase:
    """安�Eな変換クラスのファクトリ関数

    Args:
        transformer_class: 生�Eする変換クラス
        config: 変換設定辞書

    Returns:
        生�Eされた変換クラスのインスタンス

    Raises:
        ValidationError: 無効なクラスまた�E設定�E場吁E        TransformationError: インスタンス生�Eに失敗した場吁E    """
    try:
        # EAFPスタイル: まずインスタンス生�Eを試衁E        if not issubclass(transformer_class, TransformationBase):
            raise ValidationError(
                f"変換クラスは TransformationBase を継承する忁E��がありまぁE {transformer_class.__name__}"
            )

        instance = transformer_class(config)

        # 生�Eされたインスタンスの検証
        if not is_text_transformer(instance):
            raise ValidationError(
                f"生�Eされたインスタンスが�Eロトコルを実裁E��てぁE��せん: {type(instance).__name__}"
            )

        return instance

    except ValidationError:
        raise
    except Exception as e:
        raise TransformationError(
            f"変換クラスのインスタンス生�Eに失敁E {e}",
            {
                "class_name": transformer_class.__name__,
                "config": str(config),
                "error_type": type(e).__name__,
            },
        ) from e
