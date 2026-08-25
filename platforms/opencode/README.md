# OpenCode package

This package uses OpenCode's project-native
<code>.opencode/skills/&lt;name&gt;/SKILL.md</code> layout. Every skill has a
matching lowercase directory name, required frontmatter, and its full set of
supporting files.

## Add the package from a clone

Merge the <code>skills.paths</code> entry from
[opencode.example.json](opencode.example.json) into either your project
<code>opencode.json</code> or global
<code>~/.config/opencode/opencode.json</code>, then replace the placeholder
with the absolute path to this package's <code>.opencode/skills</code>
directory:

~~~json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "paths": [
      "/absolute/path/to/clanker-skills/platforms/opencode/.opencode/skills"
    ]
  }
}
~~~

Keep any existing <code>skills</code> configuration and extend its
<code>paths</code> array; do not replace unrelated configuration fields.

## Add it to one project instead

Copy the native <code>.opencode</code> directory into the target repository
root:

~~~bash
cp -R /absolute/path/to/clanker-skills/platforms/opencode/.opencode \
  /absolute/path/to/your-project/.opencode
~~~

If the target already has a skill with the same name, resolve that collision
deliberately instead of overwriting it.

OpenCode advertises discovered skills through its native <code>skill</code>
tool. Run <code>opencode debug skill</code>, confirm that the inventory contains
<code>writing-plans</code>, then load it by its exact skill ID. The official
[OpenCode skills documentation](https://opencode.ai/docs/skills) and
[configuration schema](https://opencode.ai/config.json) describe the project,
global, and additional-path discovery rules.
