# 软件工程作业

本仓库当前包含“代码审查 Agent”作业项目。

## 项目目录

[`code-review-agent`](./code-review-agent) 是一个基于 Python 和 DeepSeek API 的代码审查 Agent。

它提供本地网页界面，用户输入项目内代码文件路径后，Agent 会依次读取文件、执行 Python 静态分析、组织 Prompt 并调用 DeepSeek 生成审查建议。

## 主要能力

- Agent 循环：输入、工具调用、LLM 推理、结果输出
- 文件读取与 Python AST 静态分析工具
- DeepSeek API 调用与失败重试
- 最近三次审查的短期记忆
- 本地网页配置与审查页面

## 快速开始

进入项目目录后，启动网页服务：

```powershell
cd code-review-agent
python -m app.web
```

浏览器打开 `http://127.0.0.1:8000`。详细配置、使用方法和设计说明见项目内的 [README](./code-review-agent/README.md) 与 [Design](./code-review-agent/Design.md)。
