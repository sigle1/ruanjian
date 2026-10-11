"""本地 DeepSeek 配置的读取与保存。"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


@dataclass
class DeepSeekSettings:
    api_key: str = DEEPSEEK_API_KEY
    base_url: str = DEEPSEEK_BASE_URL
    model: str = DEEPSEEK_MODEL


class SettingsStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> DeepSeekSettings:
        if not self.path.is_file():
            return DeepSeekSettings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return DeepSeekSettings(str(data.get("api_key", "")), str(data.get("base_url", DEEPSEEK_BASE_URL)), str(data.get("model", DEEPSEEK_MODEL)))
        except (OSError, json.JSONDecodeError):
            return DeepSeekSettings()

    def save(self, settings: DeepSeekSettings) -> None:
        self.path.write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")
