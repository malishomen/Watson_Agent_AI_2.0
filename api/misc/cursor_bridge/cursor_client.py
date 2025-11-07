# cursor_bridge/cursor_client.py
from __future__ import annotations
import os, json, time
from typing import Any, Dict
import requests

class CursorClient:
    def __init__(self, base_url: str | None = None, token: str | None = None, map_path: str | None = None):
        self.base_url = base_url or os.environ.get("CURSOR_API_URL", "").rstrip("/")
        self.token = token or os.environ.get("CURSOR_API_KEY", "")
        self.map = self._load_map(map_path or os.path.join(os.path.dirname(__file__), "cursor_api_map.json"))
        self._auth_hdr_name, self._auth_fmt = self._parse_auth(self.map.get("auth", {}))

    @staticmethod
    def _load_map(path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _parse_auth(auth: Dict[str, Any]):
        t = auth.get("type", "none")
        if t == "header":
            return auth.get("header_name", "Authorization"), auth.get("format", "Bearer {token}")
        return None, None  # bearer/cookie РјРѕР¶РЅРѕ СЂР°СЃС€РёСЂРёС‚СЊ РїСЂРё РЅРµРѕР±С…РѕРґРёРјРѕСЃС‚Рё

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self._auth_hdr_name and self.token:
            h[self._auth_hdr_name] = self._auth_fmt.format(token=self.token)
        return h

    def call(self, action: str, **kwargs) -> Dict[str, Any]:
        ep = self.map["endpoints"].get(action)
        if not ep: 
            raise KeyError(f"Unknown action: {action}")
        path = ep["path"]
        method = ep.get("method", "POST").upper()
        url = f"{self.base_url}{path}"
        template = (self.map.get("payload_templates", {}).get(action) or {})
        payload = {}
        for key, value in template.items():
            if key in kwargs:
                payload[key] = kwargs[key]
            else:
                payload[key] = value
        resp = requests.request(method, url, headers=self._headers(), json=payload, timeout=120)
        try:
            data = resp.json()
        except Exception:
            data = {"text": resp.text}
        return {"status": resp.status_code, "data": data, "ok": resp.ok}

    # Sugar helpers
    def open_file(self, filepath: str):          return self.call("editor.open", filepath=filepath)
    def insert(self, filepath: str, position: str, text: str): return self.call("editor.insert", filepath=filepath, position=position, text=text)
    def replace(self, filepath: str, range: str, text: str):   return self.call("editor.replace", filepath=filepath, range=range, text=text)
    def save(self, filepath: str):               return self.call("editor.save", filepath=filepath)
    def create(self, filepath: str, text: str):  return self.call("files.create", filepath=filepath, text=text)
    def run_terminal(self, cwd: str, command: str): return self.call("terminal.run", cwd=cwd, command=command)
    def run_task(self, task_id: str, params: dict | None = None): return self.call("task.run", task_id=task_id, params=params or {})
    def chat(self, prompt: str):                 return self.call("chat.prompt", prompt=prompt)
    def open_project(self, root: str):           return self.call("project.open", root=root)
