import tempfile
import unittest
from pathlib import Path

from app.agent import CodeReviewAgent
from app.tools import PythonAnalysisTool, ReadFileTool


class FakeLLM:
    def ask(self, prompt: str) -> str:
        self.prompt = prompt
        return "这是模型返回的审查回答。"


class AgentTests(unittest.TestCase):
    def test_reader_rejects_file_outside_workspace(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertFalse(ReadFileTool(Path(folder)).run("../secret.py").ok)

    def test_analysis_finds_bare_except(self):
        result = PythonAnalysisTool().run("try:\n  pass\nexcept:\n  pass\n")
        self.assertIn("裸 except", result.content)

    def test_agent_returns_llm_response(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "demo.py").write_text("print('ok')\n", encoding="utf-8")
            agent = CodeReviewAgent(root, FakeLLM())
            answer = agent.review("demo.py")
        self.assertEqual(answer, "这是模型返回的审查回答。")


if __name__ == "__main__":
    unittest.main()
