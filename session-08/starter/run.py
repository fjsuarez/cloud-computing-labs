#!/usr/bin/env python3
"""Start an orchestration, follow it until it finishes, and report how long it took.

    python3 run.py fan_out                    # local: http://localhost:7071
    python3 run.py chain --chunks 4
    python3 run.py fan_out --base https://$APP.azurewebsites.net --key $KEY

Standard library only.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime


def call(method: str, url: str) -> dict:
    request = urllib.request.Request(url, method=method, data=b"" if method == "POST" else None)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def seconds_between(start: str, end: str) -> float:
    parse = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    return (parse(end) - parse(start)).total_seconds()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("orchestrator", choices=["chain", "fan_out"])
    parser.add_argument("--chunks", type=int, default=8)
    parser.add_argument("--base", default="http://localhost:7071")
    parser.add_argument("--key", help="function key; not needed locally")
    args = parser.parse_args()

    query = {"chunks": args.chunks}
    if args.key:
        query["code"] = args.key
    start_url = f"{args.base}/api/start/{args.orchestrator}?{urllib.parse.urlencode(query)}"

    began = time.monotonic()
    links = call("POST", start_url)
    print(f"instance  {links['id']}")
    print(f"status    {links['statusQueryGetUri']}\n")

    last = None
    while True:
        try:
            status = call("GET", links["statusQueryGetUri"])
        except (urllib.error.URLError, ConnectionError):
            # The host is down: in Part 3 you stop it on purpose. Keep asking.
            if last != "unreachable":
                print(f"{time.monotonic() - began:6.1f} s  host unreachable, still asking...")
                last = "unreachable"
            time.sleep(1)
            continue
        state = status["runtimeStatus"]
        if state != last:
            print(f"{time.monotonic() - began:6.1f} s  {state}")
            last = state
        if state in ("Completed", "Failed", "Terminated"):
            break
        time.sleep(0.5)

    print(f"\noutput    {json.dumps(status['output'])}")
    print(f"took      {seconds_between(status['createdTime'], status['lastUpdatedTime']):.1f} s "
          f"inside the orchestration, {time.monotonic() - began:.1f} s for you")
    sys.exit(0 if state == "Completed" else 1)


if __name__ == "__main__":
    main()
