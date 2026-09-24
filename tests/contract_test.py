"""Offline checks that the commands SKILL.md recommends still send what the skill claims.

Points ntn at a local fake Notion API (no token, no network): python3 tests/contract_test.py
"""
import http.server
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/notion-cli/SKILL.md"
LIST_BLOCKS = SKILL.parent / "scripts/list_blocks.py"
API_VERSION = "2026-03-11"  # keep in sync with SKILL.md

requests = []


def block(i):
    return {"id": f"b{i}", "type": "paragraph", "paragraph": {"rich_text": [{"plain_text": f"text {i}"}]}}


class FakeNotion(http.server.BaseHTTPRequestHandler):
    def handle_any(self):
        n = int(self.headers.get("Content-Length") or 0)
        url = urlparse(self.path)
        req = {
            "method": self.command,
            "path": url.path,
            "query": {k: v[0] for k, v in parse_qs(url.query).items()},
            "version": self.headers.get("Notion-Version"),
            "body": json.loads(self.rfile.read(n)) if n else None,
        }
        requests.append(req)
        resp = {"object": "list", "results": [], "has_more": False, "next_cursor": None}
        if self.command == "GET" and url.path.endswith("/children"):
            if req["query"].get("start_cursor") == "c2":
                resp["results"] = [block(3)]
            else:
                resp.update(results=[block(1), block(2)], has_more=True, next_cursor="c2")
        out = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    do_GET = do_POST = do_PATCH = do_DELETE = handle_any

    def log_message(self, *args):
        pass


def run(*args, stdin=subprocess.DEVNULL):
    requests.clear()
    res = subprocess.run(args, capture_output=True, text=True, stdin=stdin, timeout=20)
    return res


class Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FakeNotion)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        os.environ["NOTION_API_BASE_URL"] = f"http://127.0.0.1:{server.server_port}"
        os.environ["NOTION_API_TOKEN"] = "fake-token"
        os.environ.pop("NOTION_API_VERSION", None)

    def test_default_version_is_latest(self):
        run("ntn", "api", "v1/users/me")
        self.assertEqual(requests[0]["version"], API_VERSION, "ntn default Notion-Version changed: update SKILL.md")

    def test_query_params(self):
        run("ntn", "api", "v1/users", "page_size==100")
        self.assertEqual(requests[0]["query"], {"page_size": "100"})

    def test_inline_body_infers_post(self):
        run("ntn", "api", "v1/pages", "parent[page_id]=abc")
        self.assertEqual((requests[0]["method"], requests[0]["body"]), ("POST", {"parent": {"page_id": "abc"}}))

    def test_append_children_needs_explicit_patch(self):
        run("ntn", "api", "v1/blocks/abc/children", "-d", '{"children":[]}')
        self.assertEqual(requests[0]["method"], "POST", "ntn now infers PATCH here: drop the -X PATCH rule in SKILL.md")
        run("ntn", "api", "v1/blocks/abc/children", "-X", "PATCH", "-d", '{"children":[]}')
        self.assertEqual(requests[0]["method"], "PATCH")

    def test_body_from_file(self):
        payload = {"children": [{"paragraph": {"rich_text": [{"text": {"content": "don't break"}}]}}]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(payload, f)
        run("ntn", "api", "v1/blocks/abc/children", "-X", "PATCH", "-d", f"@{f.name}")
        os.unlink(f.name)
        self.assertEqual(requests[0]["body"], payload)

    def test_open_stdin_hangs_without_devnull(self):
        # Documents why SKILL.md says to redirect stdin in non-interactive shells.
        proc = subprocess.Popen(["ntn", "api", "v1/users/me"], stdin=subprocess.PIPE,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            proc.wait(timeout=3)
            self.fail("ntn api no longer waits on open stdin: drop the </dev/null note in SKILL.md")
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        finally:
            proc.stdin.close()

    def test_documented_flags_exist(self):
        help_text = (ROOT / "tests/ntn-help.txt").read_text()
        installed = subprocess.run(["ntn", "--version"], capture_output=True, text=True).stdout.strip()
        self.assertEqual(help_text.splitlines()[0], installed, "stale snapshot: run tests/snapshot.sh")
        flags = set(re.findall(r"(?<![\w-])--[a-z][a-z-]+", SKILL.read_text()))
        self.assertEqual(sorted(f for f in flags if f not in help_text), [])

    def test_list_blocks_paginates(self):
        res = run(sys.executable, str(LIST_BLOCKS), "abc")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(res.stdout.splitlines(), [f"[b{i}] (paragraph) text {i}" for i in (1, 2, 3)])
        self.assertEqual([r["query"].get("start_cursor") for r in requests], [None, "c2"])

    def test_list_blocks_requires_integration_token(self):
        env = {k: v for k, v in os.environ.items() if k != "NOTION_API_TOKEN"}
        res = subprocess.run([sys.executable, str(LIST_BLOCKS), "abc"], capture_output=True, text=True,
                             stdin=subprocess.DEVNULL, env=env, timeout=20)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("NOTION_API_TOKEN", res.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
