# Pi package

The repository root is a Pi package. Its `package.json` declares the native
`platforms/pi/skills` tree through `pi.skills`, so Pi can install all 16 skills
from Git without an npm publication.

## Install globally

```bash
pi install git:github.com/CanerKocak/clanker-skills@main
```

To attach the same package only to the current project, add `-l`:

```bash
pi install -l git:github.com/CanerKocak/clanker-skills@main
```

Pi loads the package's declared skills on startup. Use `/skill:writing-plans`
to test an explicit invocation, or let Pi load a skill when its description
matches the task.

## Use an existing clone instead

Add the path in [settings.example.json](settings.example.json) to either
`~/.pi/agent/settings.json` for global use or `.pi/settings.json` for one
trusted project. Pi requires trust before it loads project-local resources.
The official [Pi skills documentation](https://pi.dev/docs/latest/skills) covers
the settings and package discovery model.
