from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os, datetime, sys, traceback

HEARTBEAT = "/agent/data/heartbeat.txt"

def heartbeat(stage):
    try:
        os.makedirs(os.path.dirname(HEARTBEAT), exist_ok=True)
        with open(HEARTBEAT, "a") as f:
            f.write(f"{datetime.datetime.utcnow().isoformat()}Z {stage} env={dict(os.environ)}\n")
    except Exception:
        traceback.print_exc()

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        heartbeat(f"request {self.path}")
        body = json.dumps({
            "hello": "from claude-code running on orb",
            "path": self.path,
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "env_has_key": bool(os.environ.get("ORB_TEST_VAR")),
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a, **kw):
        pass

if __name__ == "__main__":
    heartbeat("startup")
    port = int(os.environ.get("ORB_PORT") or os.environ.get("HTTP_PORT") or os.environ.get("PORT") or "8000")
    print(f"serving on :{port}", flush=True)
    try:
        HTTPServer(("0.0.0.0", port), H).serve_forever()
    except Exception:
        heartbeat("crash:" + traceback.format_exc().replace("\n", " | "))
        raise
