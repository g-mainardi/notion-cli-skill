# Notion CLI (ntn) Agent Skill

This repository provides a skill for agentic AI coding assistants (like Google Antigravity and Claude Code) to interact with the Notion CLI (`ntn`). By installing this skill, your agent will understand how to use `ntn` to read, create, update pages, and query the Notion API directly from the terminal.

## Installation

### Antigravity

Use the Antigravity CLI plugin installation command:

```bash
# Install (or update) the skill as a plugin
agy plugin install https://github.com/g-mainardi/notion-cli-skill
```

Once installed, the plugin and its `notion-cli` skill will be automatically discovered by the agent on its next run.

### Claude Code

The repo is also a Claude Code plugin marketplace. Inside Claude Code (v2.1.275 or later):

```
/plugin install notion-cli-skill --marketplace g-mainardi/notion-cli-skill
```

Or from the shell:

```bash
claude plugin marketplace add g-mainardi/notion-cli-skill
claude plugin install notion-cli-skill@notion-cli-skill
```

To update: `claude plugin update notion-cli-skill@notion-cli-skill`.

## Usage

After installation, the agent will have access to the instructions defined in `SKILL.md` when it needs to interact with Notion. You can simply ask your agent:

- "Create a Notion page from this markdown file using the CLI."
- "Read my Notion page with ID `<page-id>`."
- "Search for 'Project Setup' in Notion."

**Note**: The agent will need access to your `NOTION_API_TOKEN` environment variable or proper authentication setup for the `ntn` CLI to work effectively.

## Structure

- `plugin.json`: Metadata defining this repository as an Antigravity plugin.
- `.claude-plugin/marketplace.json`: Makes the repository installable as a Claude Code plugin.
- `skills/notion-cli/SKILL.md`: The core instructions, examples, and knowledge the agent uses to operate the Notion CLI.
- `skills/notion-cli/scripts/list_blocks.py`: Helper that lists a page's child blocks with their IDs.
- `AGENTS.md`: Conventions for agents editing this repository.

## Acknowledgements

The core skill instructions (`skills/notion-cli/SKILL.md`) in this repository were adopted from the official [makenotion/skills](https://github.com/makenotion/skills) repository by Notion Labs, Inc.

## Contributing

Feel free to open issues or submit pull requests with additional CLI tricks, common commands, or improvements to the prompt.
