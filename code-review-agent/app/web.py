"""零依赖本地网页界面。"""

from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from .agent import CodeReviewAgent
from .config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL


PAGE = """<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>代码审查 Agent</title><style>
body{{max-width:900px;margin:48px auto;padding:0 20px;font:16px/1.65 system-ui,sans-serif;color:#152235;background:#f6f8fb}}
form{{padding:24px;background:#fff;border-radius:12px;box-shadow:0 3px 16px #d9e1ec}} input{{box-sizing:border-box;width:100%;padding:12px;border:1px solid #9aa8b8;border-radius:7px;font:inherit}}
button{{margin-top:14px;padding:10px 20px;border:0;border-radius:7px;background:#1769aa;color:#fff;font:inherit;cursor:pointer}} pre{{white-space:pre-wrap;word-wrap:break-word;padding:20px;background:#17212b;color:#e6edf3;border-radius:10px}} .hint{{color:#52606d}}
</style><body><h1>代码审查 Agent</h1><p class="hint">{status}</p><p class="hint">输入项目目录内的相对文件路径，例如 <code>examples/sample.py</code>。</p>
<form method="post"><label for="path">待审查文件</label><input id="path" name="path" value="{path}" required autofocus><button type="submit">开始审查</button></form>{result}</body></html>"""


def main() -> None:
    agent = CodeReviewAgent(Path.cwd())

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self._send(PAGE.format(path="", result="", status=_status()))

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            form = parse_qs(self.rfile.read(length).decode("utf-8"))
            file_path = form.get("path", [""])[0].strip()
            answer = agent.review(file_path) if file_path else "请输入文件路径。"
            result = f"<h2>DeepSeek 审查回答</h2><pre>{html.escape(answer)}</pre>"
            self._send(PAGE.format(path=html.escape(file_path), result=result, status=_status()))

        def _send(self, page: str) -> None:
            payload = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("网页已启动：http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _status() -> str:
    return f"DeepSeek 已配置，模型：{html.escape(DEEPSEEK_MODEL)}" if DEEPSEEK_API_KEY.strip() else "请在 app/config.py 中填写 DeepSeek API Key。"


if __name__ == "__main__":
    main()
