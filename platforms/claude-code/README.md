# Claude Code package

This is a standalone Claude Code plugin. Its `skills/` directory contains all
13 Clanker Skills and their supporting files. Claude Code namespaces plugin
skills under `clanker-skills`.

## Use from a clone

```bash
git clone https://github.com/CanerKocak/clanker-skills.git "${HOME}/clanker-skills"
claude --plugin-dir "${HOME}/clanker-skills/platforms/claude-code"
```

In Claude Code, run `/skills` to confirm discovery, then invoke a workflow such
as `/clanker-skills:writing-plans` or let Claude select a skill from its
description.

## Verify the package

Run the repository checks from the clone root:

```bash
cd /absolute/path/to/clanker-skills
python3 scripts/sync_platform_packages.py --check
python3 scripts/validate_repository.py
```

The plugin uses Claude Code's documented
[<code>skills/&lt;name&gt;/SKILL.md</code> layout](https://code.claude.com/docs/en/slash-commands)
and the <code>.claude-plugin/plugin.json</code> manifest.
