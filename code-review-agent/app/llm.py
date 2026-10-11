"""DeepSeek 原生 API 客户端，带有限次数重试。"""

from __future__ import annotations

import json
import time
from urllib import error, request

from .config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


class DeepSeekClient:
    def __init__(self, api_key: str = DEEPSEEK_API_KEY, base_url: str = DEEPSEEK_BASE_URL, model: str = DEEPSEEK_MODEL) -> None:
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.model = model

    def configured(self) -> bool:
        return bool(self.api_key)

    def ask(self, prompt: str) -> str:
        if not self.configured():
            raise RuntimeError("请先在 app/config.py 中填写 DEEPSEEK_API_KEY。")
        payload = json.dumps({
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": "你是一名严谨的 Python 代码审查助手。请用中文给出具体、可执行的建议。"},
                {"role": "user", "content": prompt},
            ],
        }).encode("utf-8")
        endpoint = f"{self.base_url}/chat/completions"
        last_error: Exception | None = None
        for attempt in range(3):
            req = request.Request(
                endpoint,
                data=payload,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with request.urlopen(req, timeout=30) as response:
                    body = json.loads(response.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"].strip()
            except (error.HTTPError, error.URLError, KeyError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(2**attempt)
        raise RuntimeError(f"DeepSeek 调用失败：{last_error}")
