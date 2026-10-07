# Code Review Agent

一个简单的代码审查 Agent，采用“输入 → 工具调用 → LLM 推理 → 输出”的循环。网页中的审查结果直接来自 DeepSeek API。

## 功能

- 网页输入代码文件路径。
- 文件读取工具安全读取项目内文本文件。
- Python 分析工具发现语法错误、裸 `except` 和过长函数。
- DeepSeek 根据代码与工具结果生成审查建议。
- 保留最近三次审查摘要作为短期记忆。
- API 请求失败时最多重试三次。

## 配置

复制 `app/config.example.py` 为 `app/config.py`，再填写：

```python
DEEPSEEK_API_KEY = "你的 DeepSeek API Key"
```

`app/config.py` 已加入 Git 忽略列表，不会上传 API Key。

## 运行

```powershell
cd "D:\桌面\软件工程\ruanjian\code-review-agent"
python -m app.web
```

浏览器打开 `http://127.0.0.1:8000`，输入 `examples/sample.py` 后点击“开始审查”。

## 测试

```powershell
python -m unittest discover -s tests -v
```
