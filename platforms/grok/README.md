# Grok Build package

This package uses Grok Build's native `.grok/skills/<name>/SKILL.md` layout.
All 13 skills remain user-invocable as slash commands and available for
automatic selection from their descriptions.

## Add the package globally

Clone the repository and merge the `paths` entry from
[config.example.toml](config.example.toml) into the `[skills]` section of
`~/.grok/config.toml`. Replace the placeholder with the absolute path to the
clone:

```toml
[skills]
paths = ["/absolute/path/to/clanker-skills/platforms/grok/.grok/skills"]
```

If your configuration already has a `[skills]` section, extend its existing
`paths` array instead of adding a second table.

## Add it to one project instead

Copy the native `.grok` directory to the target repository root:

```bash
cp -R /absolute/path/to/clanker-skills/platforms/grok/.grok \
  /absolute/path/to/your-project/.grok
```

Run `grok inspect` in the target project to verify discovery. The skills panel
or `/skills` then shows the available inventory; `/writing-plans` explicitly
invokes the planning workflow. The official
[Grok Build skills documentation](https://docs.x.ai/build/features/skills-plugins-marketplaces)
describes the native skill and plugin discovery model.
