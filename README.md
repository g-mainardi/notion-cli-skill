# Notion CLI (ntn) Agent Skill

This repository provides a skill for agentic AI coding assistants (like Google Antigravity) to interact with the Notion CLI (`ntn`). By installing this skill, your agent will understand how to use `ntn` to read, create, update pages, and query the Notion API directly from the terminal.

## Installation

To install this skill, you need to clone this repository into your agent's skills directory. For example, if you are using Antigravity, you can clone it into the global skills configuration:

```bash
# Clone the repository into your skills directory
git clone https://github.com/g-mainardi/notion-cli-skill.git ~/.gemini/config/skills/ntn
```

Once installed, the skill will be automatically discovered by the agent on its next run.

## Usage

After installation, the agent will have access to the instructions defined in `SKILL.md` when it needs to interact with Notion. You can simply ask your agent:

- "Create a Notion page from this markdown file using the CLI."
- "Read my Notion page with ID <page-id>."
- "Search for 'Project Setup' in Notion."

**Note**: The agent will need access to your `NOTION_API_TOKEN` environment variable or proper authentication setup for the `ntn` CLI to work effectively.

## Structure

- `SKILL.md`: The core instructions, examples, and knowledge the agent uses to operate the Notion CLI.

## Contributing

Feel free to open issues or submit pull requests with additional CLI tricks, common commands, or improvements to the prompt.
