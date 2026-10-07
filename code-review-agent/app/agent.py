"""代码审查 Agent：输入、推理、工具调用、模型输出。"""

from __future__ import annotations

from collections import deque
from pathlib import Path

from .llm import DeepSeekClient
from .tools import PythonAnalysisTool, ReadFileTool


class CodeReviewAgent:
    def __init__(self, workspace: Path, llm: DeepSeekClient | None = None) -> None:
        self.reader = ReadFileTool(workspace)
        self.analyzer = PythonAnalysisTool()
        self.llm = llm or DeepSeekClient()
        self.memory: deque[str] = deque(maxlen=3)

    def review(self, file_path: str) -> str:
        """Agent 循环：读取代码，再分析，最后让 LLM 生成审查结论。"""
        file_result = self.reader.run(file_path)
        if not file_result.ok:
            return f"工具调用失败：{file_result.content}"

        analysis_result = self.analyzer.run(file_result.content)
        history = "\n".join(self.memory) or "暂无历史审查。"
        prompt = (
            f"任务：审查文件 {file_path}\n\n"
            f"文件读取工具结果：\n{file_result.content}\n\n"
            f"代码分析工具结果：\n{analysis_result.content}\n\n"
            f"最近审查摘要：\n{history}\n\n"
            "请按问题严重程度排序，说明位置、风险和修改建议。"
        )
        try:
            answer = self.llm.ask(prompt)
        except RuntimeError as exc:
            return str(exc)
        self.memory.append(f"{file_path}：{answer[:160]}")
        return answer
