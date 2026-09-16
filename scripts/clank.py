#!/usr/bin/env python3
"""clank: headless installer for clanker-skills.

Clones the skills repository and wires it into agent harnesses.
Never prompts. All input comes from flags or environment:

    CLANK_REPO  skills repository URL (default: the public repo)
    CLANK_REF   branch to install (default: main)
    CLANK_DIR   clone location (default: ~/clanker-skills)

Commands: install, update, remove, status. Pass --json for
machine-readable output (agents should always use it).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

DEFAULT_REPO = "https://github.com/CanerKocak/clanker-skills.git"
DEFAULT_REF = "main"
HARNESSES = ("opencode", "pi", "grok", "claude-code", "codex")


def repo() -> str:
    return os.environ.get("CLANK_REPO", DEFAULT_REPO)


def ref() -> str:
    return os.environ.get("CLANK_REF", DEFAULT_REF)


def clone_dir(args) -> str:
    if args.dir:
        return os.path.abspath(os.path.expanduser(args.dir))
    return os.path.abspath(os.path.expanduser(os.environ.get("CLANK_DIR", "~/clanker-skills")))


def skills_path(harness: str, directory: str) -> str:
    layouts = {
        "opencode": ".opencode/skills",
        "pi": "skills",
        "grok": ".grok/skills",
        "claude-code": "skills",
        "codex": "skills",
    }
    return os.path.join(directory, "platforms", harness, layouts[harness])


def run_git(directory: str, *git_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", directory, *git_args],
        capture_output=True, text=True, timeout=300,
    )


def dirty(directory: str) -> bool:
    proc = run_git(directory, "status", "--porcelain")
    return proc.returncode != 0 or bool(proc.stdout.strip())


def read_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def add_list_entry(container: dict, *keys: str, value: str) -> bool:
    """Append value to a nested list, creating parents. True if changed."""
    node = container
    for key in keys[:-1]:
        child = node.get(key)
        if not isinstance(child, dict):
            child = {}
            node[key] = child
        node = child
    entries = node.get(keys[-1])
    if not isinstance(entries, list):
        entries = []
        node[keys[-1]] = entries
    if value in entries:
        return False
    entries.append(value)
    return True


def remove_list_entry(container: dict, *keys: str, value: str) -> bool:
    """Remove value from a nested list. True if changed."""
    node = container
    for key in keys[:-1]:
        child = node.get(key)
        if not isinstance(child, dict):
            return False
        node = child
    entries = node.get(keys[-1])
    if not isinstance(entries, list) or value not in entries:
        return False
    entries.remove(value)
    return True


def opencode_config(args) -> str:
    if args.scope == "project":
        return os.path.abspath("opencode.json")
    return os.path.join(os.path.expanduser("~"), ".config", "opencode", "opencode.json")


def pi_config(args) -> str:
    if args.scope == "project":
        return os.path.abspath(os.path.join(".pi", "settings.json"))
    return os.path.join(os.path.expanduser("~"), ".pi", "agent", "settings.json")


def grok_config(args) -> str:
    if args.scope == "project":
        return os.path.abspath(os.path.join(".grok", "config.toml"))
    return os.path.join(os.path.expanduser("~"), ".grok", "config.toml")


def wire_opencode(args, path: str) -> dict:
    config = opencode_config(args)
    data = read_json(config)
    changed = add_list_entry(data, "skills", "paths", value=path)
    if changed:
        write_json(config, data)
    return {"harness": "opencode", "config": config, "wired": True, "changed": changed}


def wire_pi(args, path: str) -> dict:
    config = pi_config(args)
    data = read_json(config)
    changed = add_list_entry(data, "skills", value=path)
    if changed:
        write_json(config, data)
    return {"harness": "pi", "config": config, "wired": True, "changed": changed}


def _grok_paths_line(lines: list) -> int | None:
    """Index of a single-line `paths = [...]` entry, if any."""
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("paths") and "=" in stripped and stripped.endswith("]"):
            return index
    return None


def _grok_entries(line: str) -> list:
    body = line.strip().split("=", 1)[1].strip()[1:-1].strip()
    if not body:
        return []
    return [entry.strip().strip('"').strip("'") for entry in body.split(",")]


def wire_grok(args, path: str) -> dict:
    config = grok_config(args)
    try:
        with open(config, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        text = ""
    if path in text:
        return {"harness": "grok", "config": config, "wired": True, "changed": False}
    lines = text.splitlines()
    at = _grok_paths_line(lines)
    if at is not None:
        indent = lines[at][: len(lines[at]) - len(lines[at].lstrip())]
        entries = _grok_entries(lines[at]) + [path]
        lines[at] = indent + "paths = [" + ", ".join(f'"{e}"' for e in entries) + "]"
    elif "[skills]" in text:
        at = next(i for i, line in enumerate(lines) if line.strip() == "[skills]")
        lines.insert(at + 1, f'paths = ["{path}"]')
    else:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("[skills]")
        lines.append(f'paths = ["{path}"]')
    os.makedirs(os.path.dirname(config) or ".", exist_ok=True)
    with open(config, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return {"harness": "grok", "config": config, "wired": True, "changed": True}


def unwire_grok(config: str, path: str) -> bool:
    try:
        with open(config, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return False
    at = _grok_paths_line(lines)
    if at is None or path not in _grok_entries(lines[at]):
        return False
    indent = lines[at][: len(lines[at]) - len(lines[at].lstrip())]
    entries = [entry for entry in _grok_entries(lines[at]) if entry != path]
    lines[at] = indent + "paths = [" + ", ".join(f'"{e}"' for e in entries) + "]"
    with open(config, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return True


def wire_claude_code(args, directory: str) -> dict:
    command = (
        f'claude --plugin-dir "{os.path.join(directory, "platforms", "claude-code")}"'
    )
    return {
        "harness": "claude-code",
        "wired": False,
        "changed": False,
        "manual_step": f"Launch Claude Code with: {command}",
    }


def wire_codex(args, directory: str) -> dict:
    url = repo()
    match = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
    slug = match.group(1) if match else url
    command = f"codex plugin marketplace add {slug} --ref {ref()}"
    binary = shutil.which("codex")
    if binary is None:
        return {"harness": "codex", "wired": False, "changed": False, "manual_step": f"Run: {command}"}
    proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
    return {
        "harness": "codex",
        "wired": proc.returncode == 0,
        "changed": proc.returncode == 0,
        "detail": (proc.stdout + proc.stderr).strip()[-500:],
    }


WIRERS = {
    "opencode": lambda args, d: wire_opencode(args, skills_path("opencode", d)),
    "pi": lambda args, d: wire_pi(args, skills_path("pi", d)),
    "grok": lambda args, d: wire_grok(args, skills_path("grok", d)),
    "claude-code": wire_claude_code,
    "codex": wire_codex,
}


def ensure_clone(args) -> dict:
    directory = clone_dir(args)
    if os.path.isdir(os.path.join(directory, ".git")):
        return {"dir": directory, "cloned": False}
    if os.path.exists(directory):
        return {"dir": directory, "cloned": False, "error": f"{directory} exists and is not a git clone"}
    proc = subprocess.run(
        ["git", "clone", "--branch", ref(), repo(), directory],
        capture_output=True, text=True, timeout=600,
    )
    if proc.returncode != 0:
        return {"dir": directory, "cloned": False, "error": proc.stderr.strip()[-500:]}
    return {"dir": directory, "cloned": True}


def cmd_install(args) -> tuple[dict, int]:
    state = ensure_clone(args)
    if state.get("error"):
        return state, 1
    results = []
    for harness in args.harness:
        try:
            results.append(WIRERS[harness](args, state["dir"]))
        except OSError as exc:
            results.append({"harness": harness, "wired": False, "changed": False, "error": str(exc)})
    state["harnesses"] = results
    code = 1 if any("error" in r for r in results) else 0
    return state, code


def cmd_update(args) -> tuple[dict, int]:
    directory = clone_dir(args)
    if not os.path.isdir(os.path.join(directory, ".git")):
        return {"dir": directory, "error": "not a clank clone; run install first"}, 1
    if dirty(directory):
        return {"dir": directory, "error": "working tree is dirty; commit or stash first"}, 1
    fetch = run_git(directory, "fetch", "origin")
    if fetch.returncode != 0:
        return {"dir": directory, "error": fetch.stderr.strip()[-500:]}, 1
    merge = run_git(directory, "merge", "--ff-only", f"origin/{ref()}")
    if merge.returncode != 0:
        return {"dir": directory, "error": merge.stdout.strip()[-500:] or "non-fast-forward; reclone or resolve by hand"}, 1
    current = run_git(directory, "rev-parse", "--short", "HEAD")
    return {"dir": directory, "updated": True, "head": current.stdout.strip()}, 0


def cmd_remove(args) -> tuple[dict, int]:
    directory = clone_dir(args)
    results = []
    for harness in args.harness:
        path = skills_path(harness, directory)
        if harness == "opencode":
            config = opencode_config(args)
            data = read_json(config)
            changed = remove_list_entry(data, "skills", "paths", value=path)
            if changed:
                write_json(config, data)
            results.append({"harness": harness, "unwired": True, "changed": changed})
        elif harness == "pi":
            config = pi_config(args)
            data = read_json(config)
            changed = remove_list_entry(data, "skills", value=path)
            if changed:
                write_json(config, data)
            results.append({"harness": harness, "unwired": True, "changed": changed})
        elif harness == "grok":
            changed = unwire_grok(grok_config(args), path)
            results.append({"harness": harness, "unwired": True, "changed": changed})
        else:
            results.append({"harness": harness, "unwired": True, "changed": False, "note": "nothing was auto-wired"})
    state: dict = {"dir": directory, "harnesses": results}
    if args.purge:
        if not os.path.isdir(directory):
            state["purged"] = False
        elif dirty(directory) and not args.force:
            state["purged"] = False
            state["error"] = "clone is dirty; pass --force to delete anyway"
            return state, 1
        else:
            shutil.rmtree(directory, ignore_errors=False)
            state["purged"] = True
    return state, 0


def cmd_status(args) -> tuple[dict, int]:
    directory = clone_dir(args)
    state: dict = {"dir": directory, "repo": repo(), "ref": ref()}
    if os.path.isdir(os.path.join(directory, ".git")):
        head = run_git(directory, "rev-parse", "--short", "HEAD")
        state["clone"] = True
        state["head"] = head.stdout.strip()
        state["dirty"] = dirty(directory)
    else:
        state["clone"] = False
        return state, 0
    checks = []
    for harness in args.harness:
        path = skills_path(harness, directory)
        if harness == "opencode":
            data = read_json(opencode_config(args))
            entries = data.get("skills", {}).get("paths", []) if isinstance(data.get("skills"), dict) else []
            checks.append({"harness": harness, "wired": path in entries})
        elif harness == "pi":
            data = read_json(pi_config(args))
            entries = data.get("skills", []) if isinstance(data.get("skills"), list) else []
            checks.append({"harness": harness, "wired": path in entries})
        elif harness == "grok":
            try:
                with open(grok_config(args), encoding="utf-8") as handle:
                    checks.append({"harness": harness, "wired": path in handle.read()})
            except OSError:
                checks.append({"harness": harness, "wired": False})
        else:
            checks.append({"harness": harness, "wired": "manual"})
    state["harnesses"] = checks
    return state, 0


def parse_harness(value: str) -> list[str]:
    names = [name.strip() for name in value.split(",") if name.strip()]
    unknown = [name for name in names if name not in HARNESSES]
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown harness: {', '.join(unknown)} (choose from {', '.join(HARNESSES)})")
    return names or list(HARNESSES)


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dir", default=None, help="clone location (default: $CLANK_DIR or ~/clanker-skills)")
    common.add_argument("--harness", type=parse_harness, default=list(HARNESSES),
                        help=f"comma list from {', '.join(HARNESSES)} (default: all)")
    common.add_argument("--scope", choices=("global", "project"), default="global",
                        help="wire user-wide or into the current project (default: global)")
    common.add_argument("--json", action="store_true", help="machine-readable output")
    parser = argparse.ArgumentParser(prog="clank", parents=[common],
                                     description="Headless installer for clanker-skills. Never prompts.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install", parents=[common], help="clone the repo and wire the harnesses")
    sub.add_parser("update", parents=[common], help="fast-forward the clone")
    rm = sub.add_parser("remove", parents=[common], help="unwire the harnesses")
    rm.add_argument("--purge", action="store_true", help="also delete the clone")
    rm.add_argument("--force", action="store_true", help="allow purging a dirty clone")
    sub.add_parser("status", parents=[common], help="report clone and wiring state")
    return parser


def emit(state: dict, code: int, as_json: bool) -> int:
    if as_json:
        print(json.dumps(state, indent=2))
    else:
        for key, value in state.items():
            print(f"{key}: {value}")
    return code


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    commands = {"install": cmd_install, "update": cmd_update, "remove": cmd_remove, "status": cmd_status}
    try:
        state, code = commands[args.command](args)
    except (OSError, subprocess.SubprocessError) as exc:
        state, code = {"error": str(exc)}, 1
    return emit(state, code, args.json)


if __name__ == "__main__":
    sys.exit(main())
