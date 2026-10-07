# 设计说明

## Agent 循环

1. 用户在网页输入待审查文件路径。
2. Agent 调用文件读取工具获得源代码。
3. Agent 调用 Python 分析工具得到可解释的静态发现。
4. Agent 将源代码、工具结果和最近审查摘要组成 Prompt。
5. DeepSeek API 返回审查建议，网页直接展示该回答。

## 组件职责

- `app/web.py`：网页交互入口。
- `app/agent.py`：组织输入、工具调用、记忆和模型调用。
- `app/tools.py`：文件读取与 Python 静态分析。
- `app/llm.py`：DeepSeek HTTP 调用和指数退避重试。
- `app/config.py`：唯一配置入口。

## 边界处理

文件工具限制在项目目录内，拒绝二进制文件和超过 200 KB 的文件。LLM 请求失败后会返回明确错误，不会生成伪造的本地审查结论。
