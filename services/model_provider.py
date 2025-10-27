"""model_provider.py
大模型抽象层，自动检测 OPENAI_API_KEY。
当 provider='openai' 且配置正确时调用 OpenAI ChatCompletion，否则返回 mock。
"""
from __future__ import annotations

import os
from typing import Any, Dict

# openai 为可选依赖，运行时若无需真实调用可不安装
try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover
    openai = None  # noqa: N816


class ModelProvider:
    """封装大模型调用，方便统一替换

    参数
    ------
    provider: str | None
        指定大模型提供方。目前支持 ``mock`` 与 ``openai``，
        若为 ``None`` 则根据是否存在 ``OPENAI_API_KEY`` 环境变量自动推断。
    """

    def __init__(self, provider: str | None = None):
        # 自动推断 provider
        self.provider = provider or ("openai" if os.getenv("OPENAI_API_KEY") else "mock")

        # 如果选用 openai 且库可用，则初始化 api_key
        if self.provider == "openai":
            if openai is None:
                # 未安装 openai 库，回退至 mock
                print("[ModelProvider] openai 库未安装，回退至 mock 模式")
                self.provider = "mock"
            else:
                openai.api_key = os.getenv("OPENAI_API_KEY")
                if not openai.api_key:
                    print("[ModelProvider] 未检测到 OPENAI_API_KEY，回退至 mock 模式")
                    self.provider = "mock"

    # ------------------------------------------------------------------
    # 对外统一接口
    # ------------------------------------------------------------------
    def generate(self, prompt: str, context: Dict[str, Any] | None = None) -> str:
        """根据 ``prompt`` 与 ``context`` 生成文本

        1. 当 ``provider`` = ``openai`` 且配置正确时调用 OpenAI ChatCompletion
        2. 其余情况返回 mock 文本，避免后端报错
        """
        if self.provider == "openai" and openai is not None:
            try:
                messages = [
                    {"role": "system", "content": "你是专业的金融理财顾问。"},
                    {"role": "user", "content": prompt},
                ]
                if context:
                    messages.append({"role": "user", "content": str(context)})

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                )
                return response.choices[0].message.content.strip()
            except Exception as exc:  # pragma: no cover
                # 打印错误并回退到 mock 结果，避免接口整体失败
                print(f"[ModelProvider] OpenAI 调用失败: {exc}")

        # 默认 mock 返回
        ellipsis_prompt = prompt[:20] + ("..." if len(prompt) > 20 else "")
        return f"[MOCK_MODEL_REPLY] prompt={ellipsis_prompt} context={context}"