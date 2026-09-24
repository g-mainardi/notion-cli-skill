# AGENTS.md

Guidance for AI agents working in this repository.

## What this repo is

An agent skill that teaches coding assistants to use the Notion CLI (`ntn`).
It is packaged as a plugin for Google Antigravity (`agy`) and also used as a
Claude Code skill. The core content was adopted from
[makenotion/skills](https://github.com/makenotion/skills) (MIT, see `LICENSE.md`).

There is no build and there are no dependencies beyond `ntn` and Python 3. The
product is the text of `SKILL.md` plus one helper script.

## Layout

- `plugin.json`: Antigravity plugin metadata (name only).
- `.claude-plugin/marketplace.json`: makes the repo a Claude Code marketplace
  whose single plugin is the repo root (`"source": "./"`).
- `skills/notion-cli/SKILL.md`: the skill itself: frontmatter (`name`,
  `description`) plus the instructions the agent reads.
- `skills/notion-cli/scripts/list_blocks.py`: stdlib-only helper that lists the
  child blocks of a page/block (IDs, types, text previews) through `ntn api`.
- `tests/`: offline checks, free and deterministic (see Testing).
- `evals/`: `claude plugin eval` cases that measure how Claude uses the skill.
- `README.md`: human-facing install and usage notes.

## Where the skill is installed

Editing this repo does not update installed copies. After pushing:

- **Antigravity / Gemini**: `agy plugin install https://github.com/g-mainardi/notion-cli-skill`.
  Always install from the repo URL, never from a local clone. It lands in
  `~/.gemini/config/plugins/notion-cli-skill`.
- **Claude Code**: installed as a plugin from this repo's own marketplace
  (`.claude-plugin/marketplace.json`). Update with
  `claude plugin update notion-cli-skill@notion-cli-skill`.

## Testing

- `python3 tests/contract_test.py`: runs the commands `SKILL.md` recommends
  against a local fake Notion API (no token, no network) and checks the method,
  path, `Notion-Version` and body `ntn` actually sends. It also checks that
  every `--flag` in `SKILL.md` exists in the help snapshot and that
  `list_blocks.py` paginates. Each assertion message says which `SKILL.md`
  claim to revisit when it fails.
- `tests/snapshot.sh`: rewrites `tests/ntn-help.txt` with `--help` for every
  `ntn` subcommand plus `ntn api ls`. Commit it; `git diff tests/ntn-help.txt` is the
  changelog `ntn` doesn't publish.
- `claude plugin eval .`: runs `evals/` (Claude Code only). Each case is a
  realistic request plus graders that check the skill fired and that the reply
  uses the right commands, against a no-plugin baseline. It costs model usage:
  iterate with `--case <name> --runs 1 --ablation none`, then confirm with the
  default three runs. Use it after changing the `description` or the guidance
  in `SKILL.md`. Graders are regex/tool checks on purpose: stable and free.

## Editing rules

- **Verify against the real CLI, not memory.** Before documenting a command or
  flag, check it with `ntn <command> --help`, `ntn api ls` or
  `ntn api <path> --help`, or add a case to `tests/contract_test.py`.
  `SKILL.md` tells agents to look things up; it should not duplicate the full
  command reference.
- **Keep `SKILL.md` portable across hosts.** Paths to bundled scripts must work
  in both Antigravity and Claude Code, so don't depend on a host-specific
  variable or install path. Guidance applies to every agent: no host-only
  sections.
- **Keep the API version in sync.** `SKILL.md` and `API_VERSION` in
  `tests/contract_test.py` state the version `ntn` sends by default (currently
  `2026-03-11`).
- **Keep the frontmatter `description` trigger-oriented.** It decides when the
  skill loads; measure changes with the evals.
- Write `SKILL.md` in English.

## Updating for a new `ntn` release

1. `ntn update`, then confirm with `ntn --version`. `ntn update` can report
   success without replacing the binary; if the version is unchanged, run
   `curl -fsSL https://ntn.dev | bash`.
2. `tests/snapshot.sh`, then read `git diff tests/ntn-help.txt`.
3. `python3 tests/contract_test.py`.
4. Update `SKILL.md` only for changes that affect how an agent should use the
   CLI, then rerun the tests.

## Commits

Conventional Commits: `docs:`, `feat:`, `fix:`, `chore:`, `test:`. The subject
line says why, not just what.
