import json
import os
import socket
from pathlib import Path

from flask import Flask, jsonify

# Configuration comes from the environment and state lives on disk — the two things a
# container image cannot hold on its own.
GREETING = os.environ.get("GREETING", "Hello from the container")
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
PORT = int(os.environ.get("PORT", "8000"))

COUNTER_FILE = DATA_DIR / "counter.json"

app = Flask(__name__)


def read_count() -> int:
    try:
        return json.loads(COUNTER_FILE.read_text())["count"]
    except (FileNotFoundError, ValueError, KeyError):
        return 0


def bump_count() -> int:
    count = read_count() + 1
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        COUNTER_FILE.write_text(json.dumps({"count": count}))
    except OSError as exc:
        app.logger.warning("could not persist counter: %s", exc)
    return count


@app.get("/")
def index():
    return jsonify(greeting=GREETING, hostname=socket.gethostname())


@app.get("/count")
def count():
    return jsonify(count=bump_count(), stored_in=str(COUNTER_FILE))


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


if __name__ == "__main__":
    print(f"listening on port {PORT}", flush=True)
    app.run(host="0.0.0.0", port=PORT)
