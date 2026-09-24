# AGENTS.md

Guidance for AI agents working in this repository.

## What this repo is

An agent skill that teaches coding assistants to use the Notion CLI (`ntn`).
It is packaged as a plugin for Google Antigravity (`agy`) and also used as a
Claude Code skill. The core content was adopted from
[makenotion/skills](https://github.com/makenotion/skills) (MIT, see `LICENSE.md`).

There is no build, no tests and no dependencies. The product is the text of
`SKILL.md` plus one helper script.

## Layout

- `plugin.json`: plugin metadata (name only).
- `skills/notion-cli/SKILL.md`: the skill itself: frontmatter (`name`,
  `description`) plus the instructions the agent reads.
- `skills/notion-cli/scripts/list_blocks.py`: stdlib-only helper that lists the
  child blocks of a page/block with IDs, types and text previews.
- `README.md`: human-facing install and usage notes.

## Where the skill is installed

Editing this repo does not update installed copies. After pushing:

- **Antigravity / Gemini**: `agy plugin install https://github.com/g-mainardi/notion-cli-skill`.
  Always install from the repo URL, never from a local clone. It lands in
  `~/.gemini/config/plugins/notion-cli-skill`.
- **Claude Code**: `~/.claude/skills/notion-cli` holds a copy of
  `skills/notion-cli/`.

## Editing rules

- **Verify against the real CLI, not memory.** Before documenting a command or
  flag, check it with `ntn <command> --help`, `ntn api ls` or
  `ntn api <path> --help`. `SKILL.md` tells agents to look things up; it should
  not duplicate the full command reference.
- **Keep `SKILL.md` portable across hosts.** Paths to bundled scripts must work
  in both Antigravity and Claude Code, so don't depend on a host-specific
  variable or install path.
- **Keep versions in sync.** The Notion API version used in `SKILL.md` examples
  (`--notion-version`) and in `list_blocks.py` (`Notion-Version` header) must
  match. The current value is `2026-03-11`.
- **Keep the frontmatter `description` trigger-oriented.** It decides when the
  skill loads.
- The "Gemini-Specific Guidelines" section is deliberately scoped to Gemini.
  Put general guidance above it.
- Write `SKILL.md` in English.

## Updating for a new `ntn` release

1. `ntn update`, then confirm with `ntn --version` or `ntn doctor`. `ntn update`
   can report success without replacing the binary. If the version is
   unchanged, run `curl -fsSL https://ntn.dev | bash`.
2. No public changelog exists. Find changes by diffing `ntn --help`,
   `ntn <subcommand> --help` and `ntn api ls` against what `SKILL.md` documents.
3. Update `SKILL.md` only for changes that affect how an agent should use the
   CLI.

## Commits

Conventional Commits: `docs:`, `feat:`, `fix:`, `chore:`. The subject line says
why, not just what.
