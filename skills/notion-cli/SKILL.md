---
name: notion-cli
description: >-
  Use the Notion CLI (`ntn`) from the shell: scripts and automations that run
  outside a chat, raw Notion API calls (`ntn api`), block-level edits such as
  callouts, toggles or inserting after a specific block, data source queries,
  file uploads and Notion workers. Use when the user mentions `ntn`, the Notion
  CLI, the terminal or a script, asks to "call the Notion API", "insert a block
  after a heading", "upload a file to Notion" or "deploy a worker", or when a
  connected Notion MCP server lacks the tool or plan access for the task. For
  conversational reading, searching or editing of pages, prefer a connected
  Notion MCP server if there is one.
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

Most commands accept `--json` (machine-readable) or `--plain` (tab-separated,
no headers): use them when you need to parse the output.

## CLI or Notion MCP

If a Notion MCP server is also connected, split the work:

- **MCP**: searching the workspace and reading or writing pages during a
  conversation. It acts as the user and sees the whole workspace.
- **`ntn`**: scripts and anything that runs outside a chat, endpoints the MCP
  doesn't expose or the user's plan restricts, inserting blocks after a
  specific block, file uploads, workers, and edits that should be attributed
  to the integration rather than the user.

## Install & Update

```bash
# Install
curl -fsSL https://ntn.dev | bash

# Update to latest version
ntn update
```

`ntn update` can report success (`current  latest  true`) without actually
replacing the binary. Verify with `ntn --version` afterward; if it didn't
change, rerun the install script.

## Authentication

Act through the Notion integration token, never through the user's own login,
so Notion attributes your edits to the integration and the user can tell them
apart from their own.

- The CLI uses `NOTION_API_TOKEN` when it is set, and it takes precedence over
  any stored login. Check it is set before any call that touches content.
- If it is not set, stop and ask the user for the token (it may live in a
  `.env` they can `source`). Do not run `ntn login` or fall back to stored
  login credentials: those act as the user.
- Exception: `ntn workers` commands use the `ntn login` session. Ask the user
  before running them.
- The integration only sees pages and databases shared with it (page menu →
  Connections). A `404 object_not_found` on a page that exists usually means
  it isn't shared with the integration.

## Diagnostics

If you encounter issues with credentials or configuration, use these commands:
- `ntn doctor` — Check the health of your Notion CLI setup.
- `ntn auth` — Inspect authentication credentials.
- `ntn whoami` — Show the authenticated Notion user.

## `ntn api`

Run `ntn api --help` for full syntax. Quick summary:

```bash
# GET with query param
ntn api v1/users page_size==100

# POST with inline body fields
ntn api v1/pages parent[page_id]=abc123

# POST with JSON body
ntn api v1/pages -d '{"parent":{"page_id":"abc123"}}'

# JSON body from a file (avoids shell-quoting problems with apostrophes)
ntn api v1/pages -d @payload.json
```

- The method is inferred (GET by default, POST when a body is present).
  Override with `-X METHOD`.
- The CLI sends the latest API version by default (`2026-03-11`), so
  `--notion-version` is only needed to pin an older one.
- When stdin is not a terminal (scripts, background jobs), `ntn api` reads a
  JSON body from it and can wait forever. Add `</dev/null` to calls without a
  body in those contexts.

## Pages as Markdown

Prefer `ntn pages create` / `ntn pages edit` for Markdown page content. Use
the `markdown` field when creating or updating comments via `ntn api`.

```bash
# Comment with markdown
ntn api v1/comments -d '{"parent":{"page_id":"abc123"},"markdown":"Here is a [link](https://example.com) and **bold text**."}'

# Page with markdown body
ntn pages create --parent page:abc123 --content '## Heading\n\nSome *formatted* content.'

# Edit a page
ntn pages edit <page-id> --content '## Updated Heading\n\nUpdated content.'
```

- `ntn pages get` prepends page properties as YAML frontmatter. `create` and
  `edit` strip a leading frontmatter block, so `get` output can be edited and
  fed back in. On create, a frontmatter `title` sets the page title.
- `ntn pages edit` replaces the whole page content. It refuses to delete child
  pages or databases unless you pass `--allow-deleting-content`. On shared or
  complex pages, prefer targeted block edits (below) over a full rewrite.
- If `ntn pages get` warns that the Markdown is truncated, rerun it with
  `--json` and inspect `unknown_block_ids`.
- The `markdown` field supports inline formatting (bold, italic, code, links).
  Only fall back to `rich_text` for what Markdown cannot express (mentions,
  custom emoji, colors).

## Callouts, toggles and targeted block edits

Markdown conversion turns `>` into a Quote block and has no syntax for
callouts. For callouts, toggles, or inserting blocks at a specific spot, use
the blocks API.

- **Append children with `-X PATCH`.** `v1/blocks/<id>/children` only accepts
  PATCH, but `ntn api` infers POST when a body is present, which fails with
  `400 invalid_request_url`.
- **Put the payload in a file** and pass it with `-d @payload.json`. Inline
  JSON breaks as soon as the text contains a single quote.
- **Choose the position** with a `position` object: `{"type": "start"}`,
  `{"type": "end"}` (default), or
  `{"type": "after_block", "after_block": {"id": "<block-id>"}}`. The old
  `after` parameter is deprecated.
- **Find block IDs** with the helper script that ships next to this
  `SKILL.md`: `python3 <this skill's directory>/scripts/list_blocks.py <PAGE_OR_BLOCK_ID>`
  prints one line per child block with its ID, type and a text preview. To
  see a block's exact JSON shape, run `ntn api v1/blocks/<BLOCK_ID>`.

Example: add a callout at the top of a page. `payload.json`:

```json
{
  "children": [
    {
      "type": "callout",
      "callout": {
        "rich_text": [{ "type": "text", "text": { "content": "Don't forget the review." } }],
        "icon": { "type": "emoji", "emoji": "💡" },
        "color": "blue_background"
      }
    }
  ],
  "position": { "type": "start" }
}
```

```bash
ntn api v1/blocks/<PAGE_ID>/children -X PATCH -d @payload.json && rm payload.json
```

## `ntn datasources`

Accepts a data source ID, a database ID, or a Notion URL. A database ID or URL
resolves to its single data source; if a database has several, list them with
`resolve` and query one by ID.

```bash
ntn datasources query <id-or-url> --limit 50
ntn datasources query <id-or-url> --filter '{"property":"Done","checkbox":{"equals":true}}' --sort 'Due desc'
ntn datasources query <id-or-url> --start-cursor <cursor> --json
ntn datasources resolve <database-id>
```

## `ntn files`

Convenience wrapper around the File Uploads API.

```bash
ntn files create < image.png
ntn files create --external-url https://example.com/photo.png
ntn files list          # first page only; no pagination yet
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

`ntn workers new --template workflow` is a closed alpha. Warn the user and
confirm they have access before using it; only then pass
`--user-is-in-workflows-alpha` in non-interactive shells.
