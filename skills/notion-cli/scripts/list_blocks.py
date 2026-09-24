"""List the child blocks of a Notion page or block: one line per block with ID, type and text preview."""
import json
import os
import subprocess
import sys


def fetch_children(block_id):
    cursor = None
    while True:
        cmd = ["ntn", "api", f"v1/blocks/{block_id}/children", "page_size==100"]
        if cursor:
            cmd.append(f"start_cursor=={cursor}")
        # stdin=DEVNULL: ntn api reads a JSON body from a non-TTY stdin and would wait forever.
        res = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if res.returncode != 0:
            sys.exit(f"ntn api failed: {res.stderr.strip() or res.stdout.strip()}")
        page = json.loads(res.stdout)
        yield from page.get("results", [])
        if not page.get("has_more"):
            return
        cursor = page["next_cursor"]


def preview(block):
    data = block.get(block["type"], {})
    text = "".join(t.get("plain_text", "") for t in data.get("rich_text", [])).strip()
    if not text:
        text = {"divider": "---"}.get(block["type"], data.get("title", ""))
    return text if len(text) <= 80 else text[:77] + "..."


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: list_blocks.py <PAGE_OR_BLOCK_ID>")
    if not os.environ.get("NOTION_API_TOKEN"):
        sys.exit("NOTION_API_TOKEN is not set: refusing to fall back to the user's own ntn login")
    for b in fetch_children(sys.argv[1]):
        print(f"[{b['id']}] ({b['type']}) {preview(b)}")


if __name__ == "__main__":
    main()
