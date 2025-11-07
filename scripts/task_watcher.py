import time, json, os, glob, requests

INBOX = os.path.join(os.path.dirname(__file__), "..", "inbox")
API   = os.getenv("WATSON_API_BASE", "http://127.0.0.1:8090")

def main():
    os.makedirs(INBOX, exist_ok=True)
    print(f"👀 Watching: {os.path.abspath(INBOX)}")
    while True:
        for p in sorted(glob.glob(os.path.join(INBOX, "*.task.json"))):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data.setdefault("dry_run", False)
                r = requests.post(f"{API}/relay/submit", json=data, timeout=600)
                head = r.text[:800].replace("\r","")
                print(f"\n➡ {os.path.basename(p)} → {r.status_code}\n{head}\n")
            except Exception as e:
                print(f"💥 {p}: {e}")
            finally:
                try: os.remove(p)
                except: pass
        time.sleep(2)

if __name__ == "__main__":
    main()


