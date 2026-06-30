---
name: ntn
description: A skill that provides instructions and usage examples for the Notion CLI (ntn), including authentication and managing pages.
---

# Notion CLI (ntn) Skill

## Overview
`ntn` is the official (Beta) Notion CLI used to interact with Notion workspaces directly from the terminal. It supports managing pages, querying the API, managing workers, and more.

## Authentication
The CLI primarily uses two forms of authentication:
1. **Internal OAuth**: Via `ntn login` (or `ntn login --no-browser`). This stores the auth token in the OS keyring by default, or in `~/.config/notion/auth.json` if `NOTION_KEYRING=0` is set.
2. **Public API Token**: For certain features (like `ntn pages`), the CLI explicitly requires a `NOTION_API_TOKEN` environment variable containing a Notion Integration Token.

## Key Commands

### Managing Pages
To create a page from a Markdown file:
```bash
NOTION_API_TOKEN=your_token ntn pages create --parent <parent-page-or-db-id> < document.md
```

To get a page as Markdown:
```bash
NOTION_API_TOKEN=your_token ntn pages get <page-id>
```

To update a page:
```bash
NOTION_API_TOKEN=your_token ntn pages update <page-id> < document.md
```

### Searching and API
You can query the public API directly using the `ntn api` command:
```bash
NOTION_API_TOKEN=your_token ntn api post v1/search --data '{"query":"My Page Name"}'
```

## Useful Environment Variables
- `NOTION_API_TOKEN`: Essential for interacting with `ntn pages` and the public API.
- `NOTION_KEYRING=0`: Useful in headless environments to fallback to file-based auth (`auth.json`) instead of the OS DBus secret service.
- `NOTION_WORKSPACE_ID`: Targets a specific workspace if the user belongs to multiple.
