"""带有 DeepSeek 配置表单的本地网页入口。"""

from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from .agent import CodeReviewAgent
from .llm import DeepSeekClient
from .settings import DeepSeekSettings, SettingsStore


PAGE = """<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>代码审查 Agent</title><style>
body{{max-width:900px;margin:48px auto;padding:0 20px;font:16px/1.65 system-ui,sans-serif;color:#152235;background:#f6f8fb}}
section,form{{margin:18px 0;padding:24px;background:#fff;border-radius:12px;box-shadow:0 3px 16px #d9e1ec}}
input{{box-sizing:border-box;width:100%;margin:5px 0 12px;padding:12px;border:1px solid #9aa8b8;border-radius:7px;font:inherit}}
button{{margin-top:4px;padding:10px 20px;border:0;border-radius:7px;background:#1769aa;color:#fff;font:inherit;cursor:pointer}}
pre{{white-space:pre-wrap;word-wrap:break-word;padding:20px;background:#17212b;color:#e6edf3;border-radius:10px}} .hint{{color:#52606d}}
</style><body><h1>代码审查 Agent</h1><p class="hint">{status}</p>
<section><h2>DeepSeek 配置</h2><form method="post" action="/settings"><label>API Key</label><input type="password" name="api_key" placeholder="已配置时留空即可"><label>接口地址</label><input name="base_url" value="{base_url}"><label>模型</label><input name="model" value="{model}"><button type="submit">保存配置</button></form>{saved}</section>
<form method="post" action="/review"><label for="path">待审查文件</label><input id="path" name="path" value="{path}" placeholder="examples/sample.py" required autofocus><button type="submit">开始审查</button></form>{result}</body></html>"""


def main() -> None:
    workspace = Path.cwd()
    store = SettingsStore(workspace / ".agent_settings.json")
    state = {"settings": store.load(), "saved": False}
    agent = CodeReviewAgent(workspace, _client(state["settings"]))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self._send(_page(state))

        def do_POST(self) -> None:  # noqa: N802
            form = _read_form(self)
            if self.path == "/settings":
                old: DeepSeekSettings = state["settings"]
                settings = DeepSeekSettings(
                    form.get("api_key", [""])[0].strip() or old.api_key,
                    form.get("base_url", [old.base_url])[0].strip() or old.base_url,
                    form.get("model", [old.model])[0].strip() or old.model,
                )
                store.save(settings)
                state["settings"] = settings
                state["saved"] = True
                agent.llm = _client(settings)
                self._send(_page(state))
                return
            if self.path == "/review":
                path = form.get("path", [""])[0].strip()
                answer = agent.review(path) if path else "请输入文件路径。"
                self._send(_page(state, path, f"<h2>DeepSeek 审查回答</h2><pre>{html.escape(answer)}</pre>"))
                return
            self.send_error(404)

        def _send(self, page: str) -> None:
            body = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

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


def _read_form(handler: BaseHTTPRequestHandler) -> dict[str, list[str]]:
    length = int(handler.headers.get("Content-Length", "0"))
    return parse_qs(handler.rfile.read(length).decode("utf-8"))


def _client(settings: DeepSeekSettings) -> DeepSeekClient:
    return DeepSeekClient(settings.api_key, settings.base_url, settings.model)


def _page(state: dict, path: str = "", result: str = "") -> str:
    settings: DeepSeekSettings = state["settings"]
    status = f"DeepSeek 已配置，模型：{html.escape(settings.model)}" if settings.api_key else "请在下方保存你的 DeepSeek 配置。"
    saved = "<p class=\"hint\">配置已保存到本机。</p>" if state["saved"] else ""
    return PAGE.format(status=status, base_url=html.escape(settings.base_url), model=html.escape(settings.model), path=html.escape(path), result=result, saved=saved)


if __name__ == "__main__":
    main()
