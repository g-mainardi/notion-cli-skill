---
name: notion-cli
description: >-
  Use the Notion CLI (`ntn`) to interact with the Notion API, manage workers,
  and upload files. Use when the user asks to "call the Notion API", "deploy a
  worker", "upload a file to Notion", "create a page", "query a database", or
  any task involving the `ntn` command.
---

# Notion CLI

## Look things up before answering

The CLI is self-documenting. Always prefer running these commands over guessing
syntax or relying on memorized knowledge:

- `ntn api ls` — list every public API endpoint.
- `ntn api <path> --help` — show methods, doc links, and usage for an endpoint.
- `ntn api <path> --docs` — print the full official docs for an endpoint.
- `ntn api <path> --spec` — print a reduced OpenAPI fragment (useful for
  understanding request/response schemas).
- `ntn pages get <page-id>` — retrieve a page as Markdown. Use this to read page
  content.
- `ntn <command> --help` — help for any command or subcommand.

## Install

```bash
curl -fsSL https://ntn.dev | bash
```

## Authentication

- The CLI automatically uses `NOTION_API_TOKEN` when it is set.
- Check `NOTION_API_TOKEN` first. If it is already set, prefer using it instead
  of telling the user to run `ntn login`.
- `ntn login` / `ntn logout` — log the CLI in or out (only use if not using
  `NOTION_API_TOKEN`). `ntn login` requires the user to visit a URL in a web
  browser.

## `ntn api`

Run `ntn api --help` for full syntax. Quick summary:

```bash
# GET with query param
ntn api v1/users page_size==100

# POST with inline body fields
ntn api v1/pages parent[page_id]=abc123

# POST with JSON body
ntn api v1/pages -d '{"parent":{"page_id":"abc123"}}'
```

The method is inferred (GET by default, POST when a body is present). Override
with `-X METHOD`.

### Markdown for pages and comments

Prefer `ntn pages create` / `ntn pages update` for Markdown page content. Use
the `markdown` field when creating or updating comments via `ntn api`.

```bash
# Comment with markdown
ntn api v1/comments -d '{"parent":{"page_id":"abc123"},"markdown":"Here is a [link](https://example.com) and **bold text**."}'

# Page with markdown body
ntn pages create --parent page:abc123 --content '## Heading\n\nSome *formatted* content.'
```

The `markdown` field supports inline formatting (bold, italic, code, links, etc.).
Only fall back to `rich_text` if you need features that Markdown cannot express (e.g. mentions, custom emoji, or colors).

## Notion Markdown Quirks & Formatting

When reading from or writing to Notion via the `ntn` CLI, keep in mind these technical details to ensure clean rendering:

1. **Strip YAML Frontmatter**: `ntn pages get` automatically prepends page properties (like the title) as YAML frontmatter (between `---`). Before pushing updates back to Notion using `ntn pages update`, you **MUST strip** this YAML frontmatter. If you fail to do so, Notion will render the `---` as literal horizontal dividers and the title as plain text.
   - **Utility Scripts**: 
     - **Clean Frontmatter**: If a page already has leftover frontmatter blocks (e.g. `title: ...`, `id: ...`, `date: ...`, or `---`), you can use this utility script to automatically clean them up:
       `python3 ~/.gemini/config/plugins/notion-cli-skill/skills/notion-cli/scripts/clean_frontmatter.py <PAGE_ID>`
     - **List Blocks**: Finding a specific block ID in the massive raw JSON payload is difficult and consumes context. Use this utility script to neatly list all child blocks of a page or block with their IDs, types, and text previews:
       `python3 ~/.gemini/config/plugins/notion-cli-skill/skills/notion-cli/scripts/list_blocks.py <PAGE_OR_BLOCK_ID>`

## Gemini-Specific Guidelines

*(Note: The following rules apply specifically to Gemini agents to ensure proper interaction with the Notion environment, and should be ignored by other AI systems).*

### Creating Advanced Blocks (Callouts, Toggles, etc.)

When interacting with Notion via the `ntn` CLI, keep in mind that standard Markdown conversion (performed by commands like `ntn pages update`) interprets the `>` character exclusively as a **Quote** block. It does not natively support extended syntax for Callouts.

To create advanced and native Notion blocks (such as **Callouts**, **Toggles**, etc.) — and demonstrate the same awareness of the Notion environment as other agents — **you must directly use the Notion JSON API** via the `ntn api` command, rather than relying solely on uploading Markdown files.

To add a Callout (or other complex blocks) to an existing page, use the `/blocks/{block_id}/children` endpoint and pass a properly formatted JSON payload. Always ensure you have loaded the Notion token first by sourcing the `.env` file.

#### Critical Lessons from Past Errors
When interacting with the `ntn api` command, adhere strictly to the following technical rules to avoid common pitfalls:

1. **Explicitly use HTTP PATCH**: When appending children to a block or page using `v1/blocks/<id>/children`, the CLI will infer a `POST` request if a body is present. However, the Notion API expects a `PATCH` request for this endpoint. You **must** explicitly override the method using `-X PATCH`, otherwise the API will return a `400 Bad Request: invalid_request_url` error.
2. **Avoid Bash Quoting Hell**: Never pass complex JSON bodies inline using single quotes (e.g., `-d '{ "content": "don't do this" }'`), as single quotes inside the text will prematurely terminate the bash string and cause syntax errors (`unexpected EOF`). Always write the JSON payload to a temporary file (e.g., `payload.json`) and pass it using command substitution: `-d "$(cat payload.json)"`.

#### Practical Example:

1. First, create your JSON payload file (e.g., `payload.json`):
```json
{
  "children": [
    {
      "object": "block",
      "type": "callout",
      "callout": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "This is a native Callout created via API!"
            }
          }
        ],
        "icon": {
          "type": "emoji",
          "emoji": "💡"
        },
        "color": "blue_background"
      }
    }
  ]
}
```

2. Then, execute the API call and clean up:
```bash
source .env && ntn api v1/blocks/<PAGE_OR_BLOCK_ID>/children -X PATCH -d "$(cat payload.json)" && rm payload.json
```

#### Golden Rules for Agents:
1. When asked to insert highlighted notes, warnings, or TL;DRs into a Notion page, prefer using the `v1/blocks` API with a JSON payload to generate a **Callout**, rather than performing a simple `replace_file_content` on the Markdown.
2. Use Markdown (with `ntn pages update`) only for long, predominantly text-based documents without specific Notion layout requirements. **Avoid full page overwrites** unless necessary; prefer patching specific blocks to prevent truncating collaborative documents or destroying complex layouts.
3. If in doubt about the JSON structure of a Notion block, you can always inspect an existing block by running `ntn api v1/blocks/<BLOCK_ID>`. Alternatively, use the `list_blocks.py` utility to quickly find block IDs without parsing raw JSON.
4. **Inserting in a specific position**: By default, blocks are appended at the end of the page/parent. To insert blocks *after* a specific existing block, you must include `"after": "<BLOCK_ID>"` in your JSON payload. **Critical:** The Notion API only supports the `after` parameter if you enforce an API version of `2022-06-28` or newer. Example: `curl -s -X PATCH ... -H "Notion-Version: 2022-06-28" -d '{"children": [...], "after": "..."}'`.

## `ntn files`

Convenience wrapper around the File Uploads API.

```bash
ntn files create < image.png
ntn files create --external-url https://example.com/photo.png
ntn files list
ntn files get <upload-id>
```

## `ntn workers`

Manage Notion workers (deploy, list, execute, etc.). Run `ntn workers --help`
for subcommands.

```bash
ntn workers new my-worker        # scaffold a new project
ntn workers deploy               # deploy from current directory
ntn workers ls                   # list workers
ntn workers exec <capability>    # execute a capability
```
