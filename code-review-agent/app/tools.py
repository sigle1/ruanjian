"""Agent 可调用的本地工具。"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    content: str


class ReadFileTool:
    """安全读取项目目录内的小型文本文件。"""

    def __init__(self, workspace: Path, max_bytes: int = 200_000) -> None:
        self.workspace = workspace.resolve()
        self.max_bytes = max_bytes

    def run(self, requested_path: str) -> ToolResult:
        supplied = Path(requested_path)
        candidate = (self.workspace / supplied).resolve() if not supplied.is_absolute() else supplied.resolve()
        try:
            candidate.relative_to(self.workspace)
        except ValueError:
            return ToolResult(False, "只能读取项目目录内的文件。")
        if not candidate.is_file():
            return ToolResult(False, f"找不到文件：{requested_path}")
        if candidate.stat().st_size > self.max_bytes:
            return ToolResult(False, "文件超过 200 KB，拒绝读取。")
        data = candidate.read_bytes()
        if b"\x00" in data:
            return ToolResult(False, "该文件是二进制文件，不能审查。")
        return ToolResult(True, data.decode("utf-8", errors="replace"))


class PythonAnalysisTool:
    """不执行代码，只分析 Python 语法树。"""

    def run(self, source: str) -> ToolResult:
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            return ToolResult(True, f"发现语法错误：第 {exc.lineno} 行，{exc.msg}")

        findings: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                findings.append(f"第 {node.lineno} 行使用裸 except，可能隐藏异常。")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = getattr(node, "end_lineno", node.lineno)
                if end - node.lineno + 1 > 50:
                    findings.append(f"函数 {node.name} 超过 50 行，可考虑拆分。")
        return ToolResult(True, "\n".join(findings) if findings else "未发现明确的静态问题。")
