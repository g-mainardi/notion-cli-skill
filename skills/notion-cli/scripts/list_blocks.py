import json
import subprocess
import argparse
import sys
import os

def get_blocks(block_id, token):
    cmd = f"curl -s \"https://api.notion.com/v1/blocks/{block_id}/children\" -H \"Authorization: Bearer {token}\" -H \"Notion-Version: 2022-06-28\""
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error fetching blocks: {res.stderr}")
        return []
    try:
        return json.loads(res.stdout).get("results", [])
    except json.JSONDecodeError:
        print("Error decoding JSON")
        return []

def main():
    parser = argparse.ArgumentParser(description="List child blocks of a Notion page/block neatly")
    parser.add_argument("block_id", help="The ID of the Notion page or block")
    args = parser.parse_args()

    token = os.environ.get("NOTION_API_TOKEN")
    if not token:
        # Try to load from .env in current directory
        if os.path.exists(".env"):
            with open(".env") as f:
                for line in f:
                    if "NOTION_API_TOKEN" in line:
                        token = line.split("=", 1)[1].strip().strip("\"'")
        if not token:
            print("NOTION_API_TOKEN not found in env or .env file.")
            sys.exit(1)

    blocks = get_blocks(args.block_id, token)
    
    if not blocks:
        print("No blocks found or error occurred.")
        return

    for b in blocks:
        b_id = b["id"]
        b_type = b["type"]
        text = ""
        
        # Try to extract plain text if it's a text-based block
        if b_type in b:
            rt = b[b_type].get("rich_text", [])
            if rt:
                text = "".join([x.get("plain_text", "") for x in rt]).strip()
            elif b_type == "divider":
                text = "---"
            elif b_type == "child_page":
                text = b[b_type].get("title", "")
        
        # Truncate text for preview
        if len(text) > 80:
            text = text[:77] + "..."
            
        print(f"[{b_id}] ({b_type}) {text}")

if __name__ == "__main__":
    main()
