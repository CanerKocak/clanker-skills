# DeepSeek Harness installation

DeepSeek Harness discovers skill bundles one level below a root:
<code>&lt;root&gt;/&lt;name&gt;/SKILL.md</code>. It scans the user root at
<code>$DSH_HOME/skills</code> (default <code>~/.dsh/skills</code>), project
roots at <code>&lt;project&gt;/.dsh/skills</code>, and shared agent roots at
<code>~/.agents/skills</code>. It reads user-global guidance from
<code>$DSH_HOME/AGENTS.md</code>.

The repository includes <code>scripts/install_deepseek_harness.py</code>. It
links the plugin's skill bundles into the user root and writes the output
contract plus routing block into <code>AGENTS.md</code>. The links point at
this checkout, so pulling the repository updates the skills without copying
them.

## Install

~~~bash
git clone https://github.com/CanerKocak/clanker-skills.git "$HOME/clanker-skills"
python3 "$HOME/clanker-skills/scripts/install_deepseek_harness.py" install --json
~~~

The installer is idempotent. Run it again after a pull to refresh the managed
<code>AGENTS.md</code> section.

## What the installer writes

| Location | Contents |
| --- | --- |
| <code>$DSH_HOME/skills/&lt;name&gt;</code> | A symlink to the matching bundle in <code>plugins/clanker-skills/skills</code> |
| <code>$DSH_HOME/AGENTS.md</code> | A managed <code>&lt;!-- clanker-skills:start --&gt;</code> block containing the repository output contract and routing section |

Existing entries with the same name are preserved rather than overwritten.
The installer reports them under <code>preserved</code> and leaves
<code>status</code> not wired until the conflict is resolved.

## Project scope

Run the command from a project root with <code>--scope project</code> to use
<code>&lt;project&gt;/.dsh/skills</code> and <code>&lt;project&gt;/AGENTS.md</code>:

~~~bash
cd /path/to/project
python3 /path/to/clanker-skills/scripts/install_deepseek_harness.py install --scope project --json
~~~

Project links point at the same checkout, so do not commit them.

## Update

~~~bash
cd "$HOME/clanker-skills"
git pull --ff-only
python3 scripts/install_deepseek_harness.py install --json
~~~

The skill links resolve through the updated checkout. Re-running the
installer refreshes the managed <code>AGENTS.md</code> block when the output
contract or routing excerpt changed.

## Manual installation

~~~bash
git clone https://github.com/CanerKocak/clanker-skills.git "$HOME/clanker-skills"
dsh_home="$DSH_HOME"
[ -n "$dsh_home" ] || dsh_home="$HOME/.dsh"
mkdir -p "$dsh_home/skills"
for skill in "$HOME"/clanker-skills/plugins/clanker-skills/skills/*; do
  ln -s "$skill" "$dsh_home/skills/$(basename "$skill")"
done
cat "$HOME/clanker-skills/AGENTS.md" >> "$dsh_home/AGENTS.md"
~~~

Append the [routing section](global-routing.md) to
<code>$DSH_HOME/AGENTS.md</code> as well, or use the installer so the managed
block stays current.

## Verify

~~~bash
python3 scripts/install_deepseek_harness.py status --json
dsh_home="$DSH_HOME"
[ -n "$dsh_home" ] || dsh_home="$HOME/.dsh"
ls -l "$dsh_home/skills"
~~~

In a DeepSeek Harness session, the skill catalog lists the linked bundles;
load one with the <code>skill</code> tool by exact name, for example
<code>writing-plans</code>. To remove the installation:

~~~bash
python3 scripts/install_deepseek_harness.py remove --json
~~~

## Limits

- The links require the checkout to stay at the linked path. Moving or
  deleting the clone breaks them.
- The installer does not copy skills, so it does not create a second source
  that can drift from the plugin.
- DeepSeek Harness watches the skills root, but a running session may need a
  new turn or a restart before it refreshes its catalog and global
  instructions.
