# Native platform packages

Each package contains the complete portable payload for the same 17 skills:
`SKILL.md`, scripts, references, templates, assets, and third-party licenses.
The portable source lives in `plugins/clanker-skills/skills`; generated mirrors
must be refreshed with `python3 scripts/sync_platform_packages.py` rather than
edited by hand.

| Platform | Native package path | Primary installation route | Verification |
| --- | --- | --- | --- |
| [Claude Code](claude-code/README.md) | `platforms/claude-code/` | `claude --plugin-dir …` | `/skills` |
| [OpenCode](opencode/README.md) | `platforms/opencode/.opencode/skills/` | `opencode.json` `skills.paths` | `opencode debug skill` |
| [Pi](pi/README.md) | `platforms/pi/skills/` | `pi install git:…` | `/skill:<name>` |
| [Grok Build](grok/README.md) | `platforms/grok/.grok/skills/` | `[skills] paths` entry | `grok inspect` |

The packages use the Agent Skills `SKILL.md` convention. Native layouts and
installation commands differ by platform; follow the platform README instead
of copying a path from another runtime.
