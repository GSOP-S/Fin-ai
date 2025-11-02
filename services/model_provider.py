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
        print(f"[ModelProvider] 使用 {self.provider} 模式")

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
                else:
                    print(f"[ModelProvider] 使用 OpenAI 模式，API Key已配置")

    # ------------------------------------------------------------------
    # 对外统一接口
    # ------------------------------------------------------------------
    def generate(self, prompt: str, context: Dict[str, Any] | None = None) -> str:
        """根据 ``prompt`` 与 ``context`` 生成文本

        1. 当 ``provider`` = ``openai`` 且配置正确时调用 OpenAI ChatCompletion
        2. 其余情况返回 mock 文本，避免后端报错
        """
        if self.provider == "openai" and openai is not None and openai.api_key:
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
                    timeout=5,  # 减少超时时间到5秒
                )
                return response.choices[0].message.content.strip()
            except Exception as exc:  # pragma: no cover
                # 打印错误并抛出异常，让上层service处理fallback
                print(f"[ModelProvider] OpenAI 调用失败: {exc}")
                raise Exception("OpenAI API调用失败")

        # 默认 mock 返回
        return self._get_mock_response(prompt, context)
    
    def _get_mock_response(self, prompt: str, context: Dict[str, Any] | None = None) -> str:
        """生成mock响应"""
        # 根据不同的prompt类型返回不同的mock响应
        if "市场" in prompt or "market" in prompt.lower():
            return "当前市场整体表现平稳，建议投资者保持理性，关注优质蓝筹股和债券配置，控制风险。"
        elif "基金" in prompt or "fund" in prompt.lower():
            return "基金投资需谨慎，建议根据自身风险承受能力选择合适的基金产品，分散投资降低风险。"
        elif "账单" in prompt or "bill" in prompt.lower():
            return "建议您定期查看账单明细，合理控制支出，提高储蓄率，建立良好的消费习惯。"
        elif "转账" in prompt or "transfer" in prompt.lower():
            return "转账时请仔细核对收款人信息，大额转账建议分批进行，确保资金安全。"
        else:
            ellipsis_prompt = prompt[:20] + ("..." if len(prompt) > 20 else "")
            return f"[MOCK_MODEL_REPLY] prompt={ellipsis_prompt} context={context}"