"""LLM 客户端抽象层，支持多种 LLM 服务和多模态消息。"""
import os
import base64
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """LLM 客户端基类。"""

    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]], temperature: float = 0.0) -> str:
        """发送消息并返回响应文本。"""

    @property
    def supports_images(self) -> bool:
        """是否支持图片输入。"""
        return False


class ClaudeClient(LLMClient):
    """Anthropic Claude API 客户端。"""

    def __init__(self, api_key: str, model: str = None, base_url: str = None):
        try:
            import anthropic
        except ImportError:
            raise ImportError("使用 Claude API 需要安装 anthropic: pip install anthropic")

        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = anthropic.Anthropic(**kwargs)
        self._model = model or "claude-sonnet-4-20250514"

    @property
    def supports_images(self) -> bool:
        return True

    def chat(self, messages: List[Dict[str, Any]], temperature: float = 0.0) -> str:
        # Claude API 需要 system 消息单独传
        system_msg = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                # system 消息可能是字符串或 content blocks
                content = msg["content"]
                if isinstance(content, str):
                    system_msg = content
                elif isinstance(content, list):
                    # 从 content blocks 中提取文本
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block["text"])
                    system_msg = "\n".join(text_parts)
            else:
                chat_messages.append(msg)

        kwargs = {
            "model": self._model,
            "max_tokens": 16384,
            "messages": chat_messages,
            "temperature": temperature,
        }
        if system_msg:
            kwargs["system"] = system_msg

        response = self._client.messages.create(**kwargs)
        text = response.content[0].text
        # 如果被截断，尝试继续
        if response.stop_reason == "max_tokens":
            logger.warning("LLM 响应被截断，尝试继续生成")
            text += self._continue_generation(chat_messages, system_msg, text, temperature)
        return text

    def _continue_generation(self, messages, system_msg, partial_text, temperature) -> str:
        """继续被截断的生成。"""
        continue_messages = messages + [
            {"role": "assistant", "content": partial_text},
            {"role": "user", "content": "请继续输出，从断点处接着写，不要重复已输出的内容。"},
        ]
        kwargs = {
            "model": self._model,
            "max_tokens": 16384,
            "messages": continue_messages,
            "temperature": temperature,
        }
        if system_msg:
            kwargs["system"] = system_msg
        try:
            response = self._client.messages.create(**kwargs)
            return response.content[0].text
        except Exception:
            return ""


class OpenAIClient(LLMClient):
    """OpenAI API 客户端（兼容 OpenAI 兼容接口）。"""

    def __init__(self, api_key: str, model: str = None, base_url: str = None):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("使用 OpenAI API 需要安装 openai: pip install openai")

        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = OpenAI(**kwargs)
        self._model = model or "gpt-4o"

    @property
    def supports_images(self) -> bool:
        return True

    def chat(self, messages: List[Dict[str, Any]], temperature: float = 0.0) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=8192,
        )
        return response.choices[0].message.content


def build_image_content_block(image_bytes: bytes, media_type: str, provider: str) -> Dict[str, Any]:
    """构建图片内容块。

    Args:
        image_bytes: 图片原始字节
        media_type: MIME 类型，如 "image/png"
        provider: 提供商格式 ("claude" 或 "openai")

    Returns:
        图片内容块字典
    """
    b64_data = base64.b64encode(image_bytes).decode("utf-8")

    if provider == "claude":
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": b64_data,
            }
        }
    else:  # openai
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{media_type};base64,{b64_data}"
            }
        }


_DEFAULTS = {
    "provider": "Xiaomi MiMo",
    "model": "mimo-v2.5",
}


def create_llm_client(
    provider: str = None,
    api_key: str = None,
    model: str = None,
    base_url: str = None,
) -> LLMClient:
    """创建 LLM 客户端实例。

    参数优先级: 函数参数 > 环境变量 > 内置默认值
    环境变量: LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_BASE_URL

    api_key 和 base_url 不提供内置默认值，必须通过参数或环境变量传入。
    """
    provider = provider or os.environ.get("LLM_PROVIDER") or _DEFAULTS["provider"]
    api_key = api_key or os.environ.get("LLM_API_KEY")
    model = model or os.environ.get("LLM_MODEL") or _DEFAULTS["model"]
    base_url = base_url or os.environ.get("LLM_BASE_URL")

    if not api_key:
        raise ValueError("未提供 API Key，请通过 --api-key 参数或 LLM_API_KEY 环境变量设置")

    provider = provider.lower().strip()

    if provider in ("claude", "anthropic"):
        return ClaudeClient(api_key=api_key, model=model, base_url=base_url)
    elif provider in ("openai", "openai-compatible"):
        return OpenAIClient(api_key=api_key, model=model, base_url=base_url)
    else:
        # 自动检测：base_url 包含 anthropic → ClaudeClient，否则 → OpenAIClient
        if base_url and "anthropic" in base_url.lower():
            return ClaudeClient(api_key=api_key, model=model, base_url=base_url)
        if base_url or (model and "gpt" in model.lower()):
            return OpenAIClient(api_key=api_key, model=model, base_url=base_url)
        return ClaudeClient(api_key=api_key, model=model)
