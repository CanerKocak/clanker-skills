# Contributing

Contributions should make a skill more accurate, easier to trigger, or easier
to verify. Keep each change narrow enough that its behavioral effect can be
reviewed directly.

## Before opening a pull request

1. Treat `plugins/clanker-skills/skills/<skill-name>/` as the canonical source.
   Do not manually edit generated mirrors under `platforms/`.
2. Preserve the package's `SKILL.md`, `agents/openai.yaml`, and any referenced
   scripts, references, templates, assets, or license files as one unit.
3. Keep the frontmatter `name` equal to the directory name. Use lowercase
   letters, numbers, and hyphens only.
4. Give `agents/openai.yaml` a specific 25–64 character short description and
   a default prompt that explicitly names `$<skill-name>`.
5. Run `python3 scripts/sync_platform_packages.py` after changing canonical
   portable content, then run `python3 scripts/sync_platform_packages.py --check`.
6. Run `python3 scripts/validate_repository.py` from the repository root.
7. Describe the user-facing contract that changed and the evidence used to
   verify it.

## Third-party material

Do not submit material that you lack permission to redistribute. Keep an
upstream license inside the affected package and update
`THIRD_PARTY_NOTICES.md` with its source, copyright holder, and license.
This repository does not currently grant a blanket license; opening a pull
request does not change that boundary.
