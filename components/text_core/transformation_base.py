"""
謚ｽ雎｡蝓ｺ蠎輔け繝ｩ繧ｹ縺ｨ繝・く繧ｹ繝亥､画鋤繝励Ο繝医さ繝ｫ縺ｮ螳夂ｾｩ

縺薙・繝｢繧ｸ繝･繝ｼ繝ｫ縺ｯ縲√☆縺ｹ縺ｦ縺ｮ繝・く繧ｹ繝亥､画鋤繧ｯ繝ｩ繧ｹ縺檎ｶ呎価縺吶∋縺肴歓雎｡蝓ｺ蠎輔け繝ｩ繧ｹ縺ｨ
蝙句ｮ牙・諤ｧ繧剃ｿ晁ｨｼ縺吶ｋ繝励Ο繝医さ繝ｫ繧呈署萓帙＠縺ｾ縺吶・"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

from .exceptions import ValidationError, TransformationError
from .types import ConfigDict, ErrorContext








class TransformationBase(ABC):
    """縺吶∋縺ｦ縺ｮ繝・く繧ｹ繝亥､画鋤繧ｯ繝ｩ繧ｹ縺ｮ謚ｽ雎｡蝓ｺ蠎輔け繝ｩ繧ｹ

    縺薙・繧ｯ繝ｩ繧ｹ縺ｯ螟画鋤蜃ｦ逅・・蜈ｱ騾壹う繝ｳ繧ｿ繝ｼ繝輔ぉ繝ｼ繧ｹ繧貞ｮ夂ｾｩ縺励・    螳溯｣・け繝ｩ繧ｹ縺悟ｿ・医Γ繧ｽ繝・ラ繧呈戟縺､縺薙→繧剃ｿ晁ｨｼ縺励∪縺吶・    """

    def __init__(self, config: ConfigDict | None = None) -> None:
        """謚ｽ雎｡蝓ｺ蠎輔け繝ｩ繧ｹ縺ｮ蛻晄悄蛹・
        Args:
            config: 螟画鋤險ｭ螳夊ｾ樊嶌・医が繝励す繝ｧ繝ｳ・・        """
        self._config: ConfigDict = config or {}
        self._is_initialized: bool = False
        self._error_context: ErrorContext = {}

    @abstractmethod
    def transform(self, text: str) -> str:
        """繝・く繧ｹ繝亥､画鋤繧貞ｮ溯｡後☆繧区歓雎｡繝｡繧ｽ繝・ラ

        Args:
            text: 螟画鋤蟇ｾ雎｡縺ｮ繝・く繧ｹ繝・
        Returns:
            螟画鋤縺輔ｌ縺溘ユ繧ｭ繧ｹ繝・
        Raises:
            TransformationError: 螟画鋤蜃ｦ逅・↓螟ｱ謨励＠縺溷ｴ蜷・        """
        ...

    @abstractmethod
    def get_transformation_rule(self) -> str:
        """驕ｩ逕ｨ縺輔ｌ繧句､画鋤繝ｫ繝ｼ繝ｫ繧貞叙蠕励☆繧区歓雎｡繝｡繧ｽ繝・ラ

        Returns:
            螟画鋤繝ｫ繝ｼ繝ｫ譁・ｭ怜・・井ｾ・ '/t', '/l', '/u'縺ｪ縺ｩ・・        """
        ...

    @abstractmethod
    def get_input_text(self) -> str:
        """螟画鋤蜑阪・譁・ｭ怜・繧貞叙蠕励☆繧区歓雎｡繝｡繧ｽ繝・ラ

        Returns:
            螟画鋤蜑阪・譁・ｭ怜・
        """
        ...

    @abstractmethod
    def get_output_text(self) -> str:
        """螟画鋤蠕後・譁・ｭ怜・繧貞叙蠕励☆繧区歓雎｡繝｡繧ｽ繝・ラ

        Returns:
            螟画鋤蠕後・譁・ｭ怜・
        """
        ...

    def validate_input(self, text: str) -> bool:
        """蜈･蜉帙ユ繧ｭ繧ｹ繝医・螯･蠖捺ｧ繧呈､懆ｨｼ

        Args:
            text: 讀懆ｨｼ蟇ｾ雎｡縺ｮ繝・く繧ｹ繝・
        Returns:
            蜈･蜉帙′螯･蠖薙↑蝣ｴ蜷・rue
        """
        try:
            return isinstance(text, str)
        except Exception:
            # EAFP繧ｹ繧ｿ繧､繝ｫ: 萓句､悶′逋ｺ逕溘＠縺溷ｴ蜷医・辟｡蜉ｹ縺ｨ縺ｿ縺ｪ縺・            return False

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """險ｭ螳壼､繧貞叙蠕・
        Args:
            key: 險ｭ螳壹く繝ｼ
            default: 繝・ヵ繧ｩ繝ｫ繝亥､

        Returns:
            險ｭ螳壼､縺ｾ縺溘・繝・ヵ繧ｩ繝ｫ繝亥､
        """
        try:
            return self._config[key]
        except KeyError:
            # EAFP繧ｹ繧ｿ繧､繝ｫ: 繧ｭ繝ｼ縺悟ｭ伜惠縺励↑縺・ｴ蜷医・繝・ヵ繧ｩ繝ｫ繝医ｒ霑斐☆
            return default

    def set_error_context(self, context: ErrorContext) -> None:
        """繧ｨ繝ｩ繝ｼ繧ｳ繝ｳ繝・く繧ｹ繝医ｒ險ｭ螳・
        Args:
            context: 繧ｨ繝ｩ繝ｼ諠・ｱ繧貞性繧霎樊嶌
        """
        import contextlib

        with contextlib.suppress(Exception):
            # EAFP繧ｹ繧ｿ繧､繝ｫ: 譖ｴ譁ｰ縺ｫ螟ｱ謨励＠縺溷ｴ蜷医・辟｡隕・            self._error_context.update(context)

    def get_error_context(self) -> ErrorContext:
        """迴ｾ蝨ｨ縺ｮ繧ｨ繝ｩ繝ｼ繧ｳ繝ｳ繝・く繧ｹ繝医ｒ蜿門ｾ・
        Returns:
            繧ｨ繝ｩ繝ｼ繧ｳ繝ｳ繝・く繧ｹ繝郁ｾ樊嶌
        """
        try:
            return self._error_context.copy()
        except Exception:
            # EAFP繧ｹ繧ｿ繧､繝ｫ: 繧ｳ繝斐・縺ｫ螟ｱ謨励＠縺溷ｴ蜷医・遨ｺ霎樊嶌繧定ｿ斐☆
            return {}

    def set_arguments(self, args: list[str]) -> None:
        """螟画鋤蜃ｦ逅・・蠑墓焚繧定ｨｭ螳夲ｼ医が繝励す繝ｧ繝ｳ繝｡繧ｽ繝・ラ・・
        Args:
            args: 螟画鋤蜃ｦ逅・↓貂｡縺吝ｼ墓焚縺ｮ繝ｪ繧ｹ繝・
        Note:
            縺薙・繝｡繧ｽ繝・ラ縺ｯ蠑墓焚繧貞ｿ・ｦ√→縺吶ｋ螟画鋤繧ｯ繝ｩ繧ｹ縺ｧ繧ｪ繝ｼ繝舌・繝ｩ繧､繝峨＆繧後ｋ
            蝓ｺ譛ｬ螳溯｣・〒縺ｯ菴輔ｂ陦後ｏ縺ｪ縺・ｼ域・遉ｺ逧・↑no-op・・        """
        # Explicit no-op: This is an optional hook method
        # Subclasses that need arguments will override this method

    def _safe_transform(self, text: str) -> str:
        """螳牙・縺ｪ螟画鋤螳溯｡後・繝倥Ν繝代・繝｡繧ｽ繝・ラ

        Args:
            text: 螟画鋤蟇ｾ雎｡縺ｮ繝・く繧ｹ繝・
        Returns:
            螟画鋤縺輔ｌ縺溘ユ繧ｭ繧ｹ繝・
        Raises:
            ValidationError: 蜈･蜉帶､懆ｨｼ縺ｫ螟ｱ謨励＠縺溷ｴ蜷・            TransformationError: 螟画鋤蜃ｦ逅・↓螟ｱ謨励＠縺溷ｴ蜷・        """
        # EAFP繧ｹ繧ｿ繧､繝ｫ: 縺ｾ縺壼､画鋤繧定ｩｦ陦後＠縲∝､ｱ謨玲凾縺ｫ隧ｳ邏ｰ讀懆ｨｼ
        try:
            if not self.validate_input(text):
                raise ValidationError(
                    f"蜈･蜉帶､懆ｨｼ縺ｫ螟ｱ謨・ {type(text).__name__}",
                    {"input_type": type(text).__name__, "input_value": str(text)[:100]},
                )

            return self.transform(text)

        except ValidationError:
            raise
        except Exception as e:
            # 螟画鋤螟ｱ謨玲凾縺ｮ繧ｨ繝ｩ繝ｼ繧ｳ繝ｳ繝・く繧ｹ繝医ｒ險ｭ螳・            self.set_error_context(
                {
                    "transform_error": str(e),
                    "error_type": type(e).__name__,
                    "input_length": len(text) if isinstance(text, str) else 0,
                }
            )
            raise TransformationError(f"螟画鋤蜃ｦ逅・↓螟ｱ謨・ {e}", self.get_error_context()) from e


@runtime_checkable
class TextTransformerProtocol(Protocol):
    """繝・く繧ｹ繝亥､画鋤蜃ｦ逅・・繝励Ο繝医さ繝ｫ螳夂ｾｩ

    縺薙・繝励Ο繝医さ繝ｫ縺ｯ螟画鋤繧ｯ繝ｩ繧ｹ縺悟ｮ溯｣・☆縺ｹ縺阪Γ繧ｽ繝・ラ繧貞ｮ夂ｾｩ縺励・    蝙句ｮ牙・諤ｧ繧剃ｿ晁ｨｼ縺励∪縺吶・    """

    def transform(self, text: str) -> str:
        """繝・く繧ｹ繝亥､画鋤繧貞ｮ溯｡・
        Args:
            text: 螟画鋤蟇ｾ雎｡縺ｮ繝・く繧ｹ繝・
        Returns:
            螟画鋤縺輔ｌ縺溘ユ繧ｭ繧ｹ繝・        """
        ...

    def validate_input(self, text: str) -> bool:
        """蜈･蜉帙ユ繧ｭ繧ｹ繝医・螯･蠖捺ｧ繧呈､懆ｨｼ

        Args:
            text: 讀懆ｨｼ蟇ｾ雎｡縺ｮ繝・く繧ｹ繝・
        Returns:
            蜈･蜉帙′螯･蠖薙↑蝣ｴ蜷・rue
        """
        ...

    def get_transformation_rule(self) -> str:
        """驕ｩ逕ｨ縺輔ｌ繧句､画鋤繝ｫ繝ｼ繝ｫ繧貞叙蠕・
        Returns:
            螟画鋤繝ｫ繝ｼ繝ｫ譁・ｭ怜・・井ｾ・ '/t', '/l', '/u'縺ｪ縺ｩ・・        """
        ...

    def get_input_text(self) -> str:
        """螟画鋤蜑阪・譁・ｭ怜・繧貞叙蠕・
        Returns:
            螟画鋤蜑阪・譁・ｭ怜・
        """
        ...

    def get_output_text(self) -> str:
        """螟画鋤蠕後・譁・ｭ怜・繧貞叙蠕・
        Returns:
            螟画鋤蠕後・譁・ｭ怜・
        """
        ...


@runtime_checkable
class ConfigurableTransformerProtocol(TextTransformerProtocol, Protocol):
    """險ｭ螳壼庄閭ｽ縺ｪ螟画鋤蜃ｦ逅・・繝励Ο繝医さ繝ｫ螳夂ｾｩ

    縺薙・繝励Ο繝医さ繝ｫ縺ｯ險ｭ螳壹ｒ謖√▽螟画鋤繧ｯ繝ｩ繧ｹ縺悟ｮ溯｣・☆縺ｹ縺・    繝｡繧ｽ繝・ラ繧貞ｮ夂ｾｩ縺励∪縺吶・    """

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """險ｭ螳壼､繧貞叙蠕・
        Args:
            key: 險ｭ螳壹く繝ｼ
            default: 繝・ヵ繧ｩ繝ｫ繝亥､

        Returns:
            險ｭ螳壼､縺ｾ縺溘・繝・ヵ繧ｩ繝ｫ繝亥､
        """
        ...

    def set_error_context(self, context: ErrorContext) -> None:
        """繧ｨ繝ｩ繝ｼ繧ｳ繝ｳ繝・く繧ｹ繝医ｒ險ｭ螳・
        Args:
            context: 繧ｨ繝ｩ繝ｼ諠・ｱ繧貞性繧霎樊嶌
        """
        ...


class ChainableTransformationBase(TransformationBase):
    """繝√ぉ繧､繝ｳ蜿ｯ閭ｽ縺ｪ螟画鋤蜃ｦ逅・・謚ｽ雎｡蝓ｺ蠎輔け繝ｩ繧ｹ

    隍・焚縺ｮ螟画鋤繧帝｣骼悶＠縺ｦ螳溯｡後〒縺阪ｋ讖溯・繧呈署萓帙＠縺ｾ縺吶・    """

    def __init__(self, config: ConfigDict | None = None) -> None:
        """繝√ぉ繧､繝ｳ蜿ｯ閭ｽ螟画鋤繧ｯ繝ｩ繧ｹ縺ｮ蛻晄悄蛹・
        Args:
            config: 螟画鋤險ｭ螳夊ｾ樊嶌・医が繝励す繝ｧ繝ｳ・・        """
        super().__init__(config)
        self._chain: list[TransformationBase] = []

    def add_transformer(self, transformer: TransformationBase) -> None:
        """螟画鋤蜃ｦ逅・ｒ繝√ぉ繧､繝ｳ縺ｫ霑ｽ蜉

        Args:
            transformer: 霑ｽ蜉縺吶ｋ螟画鋤蜃ｦ逅・        """
        try:
            if not isinstance(transformer, TransformationBase):
                raise ValidationError(
                    f"螟画鋤蜃ｦ逅・・ TransformationBase 繧堤ｶ呎価縺吶ｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・ {type(transformer).__name__}"
                )
            self._chain.append(transformer)
        except Exception as e:
            # EAFP繧ｹ繧ｿ繧､繝ｫ: 霑ｽ蜉縺ｫ螟ｱ謨励＠縺溷ｴ蜷医・繧ｨ繝ｩ繝ｼ繧定ｨ倬鹸
            self.set_error_context(
                {
                    "chain_add_error": str(e),
                    "transformer_type": type(transformer).__name__,
                }
            )
            raise

    def chain_transform(self, text: str) -> str:
        """繝√ぉ繧､繝ｳ縺輔ｌ縺溷､画鋤繧帝・ｬ｡螳溯｡・
        Args:
            text: 螟画鋤蟇ｾ雎｡縺ｮ繝・く繧ｹ繝・
        Returns:
            繝√ぉ繧､繝ｳ螟画鋤縺輔ｌ縺溘ユ繧ｭ繧ｹ繝・
        Raises:
            TransformationError: 繝√ぉ繧､繝ｳ螟画鋤縺ｫ螟ｱ謨励＠縺溷ｴ蜷・        """
        try:
            result: str = text

            for i, transformer in enumerate(self._chain):
                try:
                    result = transformer._safe_transform(result)
                except Exception as e:
                    # 繝√ぉ繧､繝ｳ蜀・・螟画鋤螟ｱ謨玲凾縺ｮ繧ｳ繝ｳ繝・く繧ｹ繝・                    self.set_error_context(
                        {
                            "chain_position": i,
                            "transformer_type": type(transformer).__name__,
                            "chain_error": str(e),
                        }
                    )
                    raise TransformationError(
                        f"繝√ぉ繧､繝ｳ螟画鋤縺ｮ隨ｬ{i+1}谿ｵ髫弱〒螟ｱ謨・ {e}",
                        self.get_error_context(),
                    ) from e

            return result

        except TransformationError:
            raise
        except Exception as e:
            raise TransformationError(
                f"繝√ぉ繧､繝ｳ螟画鋤蜃ｦ逅・↓螟ｱ謨・ {e}", self.get_error_context()
            ) from e

    def clear_chain(self) -> None:
        """螟画鋤繝√ぉ繧､繝ｳ繧偵け繝ｪ繧｢"""
        import contextlib

        with contextlib.suppress(Exception):
            # EAFP繧ｹ繧ｿ繧､繝ｫ: 繧ｯ繝ｪ繧｢縺ｫ螟ｱ謨励＠縺溷ｴ蜷医・辟｡隕・            self._chain.clear()

    def get_chain_length(self) -> int:
        """繝√ぉ繧､繝ｳ縺ｮ髟ｷ縺輔ｒ蜿門ｾ・
        Returns:
            繝√ぉ繧､繝ｳ縺ｫ蜷ｫ縺ｾ繧後ｋ螟画鋤蜃ｦ逅・・謨ｰ
        """
        try:
            return len(self._chain)
        except Exception:
            # EAFP繧ｹ繧ｿ繧､繝ｫ: 髟ｷ縺募叙蠕励↓螟ｱ謨励＠縺溷ｴ蜷医・0繧定ｿ斐☆
            return 0


def is_text_transformer(obj: Any) -> bool:
    """繧ｪ繝悶ず繧ｧ繧ｯ繝医′ TextTransformerProtocol 繧貞ｮ溯｣・＠縺ｦ縺・ｋ縺区､懆ｨｼ

    Args:
        obj: 讀懆ｨｼ蟇ｾ雎｡縺ｮ繧ｪ繝悶ず繧ｧ繧ｯ繝・
    Returns:
        繝励Ο繝医さ繝ｫ繧貞ｮ溯｣・＠縺ｦ縺・ｋ蝣ｴ蜷・rue
    """
    try:
        return isinstance(obj, TextTransformerProtocol)
    except Exception:
        # EAFP繧ｹ繧ｿ繧､繝ｫ: 讀懆ｨｼ縺ｫ螟ｱ謨励＠縺溷ｴ蜷医・False繧定ｿ斐☆
        return False


def is_configurable_transformer(obj: Any) -> bool:
    """繧ｪ繝悶ず繧ｧ繧ｯ繝医′ ConfigurableTransformerProtocol 繧貞ｮ溯｣・＠縺ｦ縺・ｋ縺区､懆ｨｼ

    Args:
        obj: 讀懆ｨｼ蟇ｾ雎｡縺ｮ繧ｪ繝悶ず繧ｧ繧ｯ繝・
    Returns:
        繝励Ο繝医さ繝ｫ繧貞ｮ溯｣・＠縺ｦ縺・ｋ蝣ｴ蜷・rue
    """
    try:
        return isinstance(obj, ConfigurableTransformerProtocol)
    except Exception:
        # EAFP繧ｹ繧ｿ繧､繝ｫ: 讀懆ｨｼ縺ｫ螟ｱ謨励＠縺溷ｴ蜷医・False繧定ｿ斐☆
        return False


def create_safe_transformer(
    transformer_class: type[TransformationBase], config: ConfigDict | None = None
) -> TransformationBase:
    """螳牙・縺ｪ螟画鋤繧ｯ繝ｩ繧ｹ縺ｮ繝輔ぃ繧ｯ繝医Μ髢｢謨ｰ

    Args:
        transformer_class: 逕滓・縺吶ｋ螟画鋤繧ｯ繝ｩ繧ｹ
        config: 螟画鋤險ｭ螳夊ｾ樊嶌

    Returns:
        逕滓・縺輔ｌ縺溷､画鋤繧ｯ繝ｩ繧ｹ縺ｮ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ

    Raises:
        ValidationError: 辟｡蜉ｹ縺ｪ繧ｯ繝ｩ繧ｹ縺ｾ縺溘・險ｭ螳壹・蝣ｴ蜷・        TransformationError: 繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ逕滓・縺ｫ螟ｱ謨励＠縺溷ｴ蜷・    """
    try:
        # EAFP繧ｹ繧ｿ繧､繝ｫ: 縺ｾ縺壹う繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ逕滓・繧定ｩｦ陦・        if not issubclass(transformer_class, TransformationBase):
            raise ValidationError(
                f"螟画鋤繧ｯ繝ｩ繧ｹ縺ｯ TransformationBase 繧堤ｶ呎価縺吶ｋ蠢・ｦ√′縺ゅｊ縺ｾ縺・ {transformer_class.__name__}"
            )

        instance = transformer_class(config)

        # 逕滓・縺輔ｌ縺溘う繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ縺ｮ讀懆ｨｼ
        if not is_text_transformer(instance):
            raise ValidationError(
                f"逕滓・縺輔ｌ縺溘う繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ縺後・繝ｭ繝医さ繝ｫ繧貞ｮ溯｣・＠縺ｦ縺・∪縺帙ｓ: {type(instance).__name__}"
            )

        return instance

    except ValidationError:
        raise
    except Exception as e:
        raise TransformationError(
            f"螟画鋤繧ｯ繝ｩ繧ｹ縺ｮ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ逕滓・縺ｫ螟ｱ謨・ {e}",
            {
                "class_name": transformer_class.__name__,
                "config": str(config),
                "error_type": type(e).__name__,
            },
        ) from e
