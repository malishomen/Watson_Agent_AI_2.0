import os, json, http.client, urllib.parse

BASE = os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:1234/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "lm-studio")


def _conn_and_path():
    parsed = urllib.parse.urlparse(BASE)
    conn = http.client.HTTPConnection(parsed.hostname, parsed.port or 80, timeout=180)
    path = parsed.path.rstrip("/") + "/chat/completions"
    return conn, path


def chat(model, messages, temperature=0.2, max_tokens=None):
    conn, path = _conn_and_path()
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    conn.request("POST", path, body=json.dumps(payload).encode("utf-8"), headers=headers)
    resp = conn.getresponse()
    data = resp.read()
    if resp.status >= 300:
        raise RuntimeError(f"LLM HTTP {resp.status}: {data[:500]}")
    j = json.loads(data.decode("utf-8", errors="ignore"))
    return j["choices"][0]["message"]["content"]


