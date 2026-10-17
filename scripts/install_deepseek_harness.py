#!/usr/bin/env python3
"""Install Clanker Skills for DeepSeek Harness.

DeepSeek Harness discovers skills from $DSH_HOME/skills (default ~/.dsh/skills)
and user-global guidance from $DSH_HOME/AGENTS.md. This script links the
plugin's skill bundles into that directory and writes the output contract plus
the global routing block into AGENTS.md. The links point at this checkout, so
pulling the repository updates the skills without copying them.

Commands: install, status, remove. Pass --json for machine-readable output.
Use --scope project from a project root to target <project>/.dsh/skills and
<project>/AGENTS.md instead of the user-global files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

BLOCK_START = "<!-- clanker-skills:start -->"
BLOCK_END = "<!-- clanker-skills:end -->"
DEFAULT_DSH_HOME = "~/.dsh"


def repo_root(value: str | None) -> Path:
    if value is not None:
        return Path(value).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def source_skills(repo: Path) -> Path:
    root = repo / "plugins" / "clanker-skills" / "skills"
    if not root.is_dir():
        raise SystemExit(f"missing skill source: {root}")
    return root


def skill_bundles(source: Path) -> list[tuple[str, Path]]:
    found = [
        (path.name, path)
        for path in sorted(source.iterdir())
        if path.is_dir() and (path / "SKILL.md").is_file()
    ]
    if not found:
        raise SystemExit(f"no skill bundles found in {source}")
    return found


def dsh_home() -> Path:
    return Path(os.environ.get("DSH_HOME") or DEFAULT_DSH_HOME).expanduser().resolve()


def destinations(args) -> tuple[Path, Path]:
    if args.scope == "project":
        root = Path.cwd().resolve()
        return root / ".dsh" / "skills", root / "AGENTS.md"
    home = dsh_home()
    return home / "skills", home / "AGENTS.md"


def link_target(link: Path) -> Path:
    raw = os.readlink(link)
    target = Path(raw)
    if not target.is_absolute():
        target = link.parent / target
    return target.resolve()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=".clanker-", delete=False
    )
    try:
        with handle:
            handle.write(text)
        os.chmod(handle.name, mode)
        os.replace(handle.name, path)
    except BaseException:
        try:
            os.unlink(handle.name)
        except OSError:
            pass
        raise


def routing_block(repo: Path) -> tuple[str, list[str]]:
    path = repo / "docs" / "global-routing.md"
    try:
        text = read_text(path)
    except OSError as exc:
        return "", [f"routing block unavailable: {exc}"]
    fence = chr(96) * 3
    opening = f"{fence}markdown\n"
    start = text.find(opening)
    if start < 0:
        return "", ["routing block: no markdown fence"]
    start += len(opening)
    end = text.find(f"\n{fence}", start)
    if end < 0:
        return "", ["routing block: unclosed markdown fence"]
    section = re.search(r"(?m)^##\s+", text[start:end])
    if section is None:
        return "", ["routing block: no section heading"]
    return text[start + section.start() : end].strip(), []


def instructions(repo: Path) -> tuple[str, list[str]]:
    routing, warnings = routing_block(repo)
    try:
        contract = read_text(repo / "AGENTS.md").strip()
    except OSError as exc:
        return routing, warnings + [f"AGENTS.md unavailable: {exc}"]
    if not contract:
        warnings.append("AGENTS.md is empty")
        return routing, warnings
    return (contract + "\n\n" + routing).strip() if routing else contract, warnings


def has_block(text: str) -> bool:
    start = text.find(BLOCK_START)
    return start >= 0 and text.find(BLOCK_END, start + len(BLOCK_START)) >= 0


def block_text(payload: str) -> str:
    return f"{BLOCK_START}\n{payload.strip()}\n{BLOCK_END}\n"


def install_block(path: Path, payload: str) -> bool:
    block = block_text(payload)
    try:
        current = read_text(path)
    except OSError:
        current = ""
    start = current.find(BLOCK_START)
    end = (
        current.find(BLOCK_END, start + len(BLOCK_START))
        if start >= 0
        else -1
    )
    if start >= 0 and end >= 0:
        after = current[end + len(BLOCK_END) :]
        if after.startswith("\n"):
            after = after[1:]
        updated = current[:start] + block + after
    else:
        prefix = current.rstrip("\n")
        updated = f"{prefix}\n\n{block}" if prefix else block
    if updated == current:
        return False
    write_text(path, updated)
    return True


def remove_block(path: Path) -> bool:
    try:
        current = read_text(path)
    except OSError:
        return False
    start = current.find(BLOCK_START)
    end = (
        current.find(BLOCK_END, start + len(BLOCK_START))
        if start >= 0
        else -1
    )
    if start < 0 or end < 0:
        return False
    remaining = (current[:start] + current[end + len(BLOCK_END) :]).strip("\n")
    if remaining:
        write_text(path, remaining + "\n")
    else:
        path.unlink()
    return True


def install(args, repo: Path) -> dict:
    source = source_skills(repo)
    skills_dir, agents_path = destinations(args)
    skills_dir.mkdir(parents=True, exist_ok=True)
    installed = []
    unchanged = 0
    preserved = []
    for name, source_dir in skill_bundles(source):
        target = skills_dir / name
        if target.is_symlink():
            if link_target(target) == source_dir.resolve():
                unchanged += 1
            else:
                preserved.append(name)
        elif target.exists():
            preserved.append(name)
        else:
            target.symlink_to(source_dir.resolve(), target_is_directory=True)
            installed.append(name)
    payload, warnings = instructions(repo)
    agents_changed = bool(payload) and install_block(agents_path, payload)
    result = {
        "command": "install",
        "scope": args.scope,
        "skills": str(skills_dir),
        "agents_md": str(agents_path),
        "total": len(installed) + unchanged + len(preserved),
        "installed": len(installed),
        "unchanged": unchanged,
        "preserved": preserved,
        "agents_md_changed": agents_changed,
        "changed": bool(installed) or agents_changed,
    }
    if warnings:
        result["warnings"] = warnings
    return result


def status(args, repo: Path) -> dict:
    source = source_skills(repo)
    skills_dir, agents_path = destinations(args)
    expected = [name for name, _ in skill_bundles(source)]
    linked = 0
    if skills_dir.is_dir():
        for name in expected:
            target = skills_dir / name
            if target.is_symlink() and link_target(target) == (source / name).resolve():
                linked += 1
    try:
        agents_installed = has_block(read_text(agents_path))
    except OSError:
        agents_installed = False
    return {
        "command": "status",
        "scope": args.scope,
        "skills": str(skills_dir),
        "linked": linked,
        "total": len(expected),
        "agents_md": str(agents_path),
        "agents_md_installed": agents_installed,
        "wired": linked == len(expected) and agents_installed,
    }


def remove(args, repo: Path) -> dict:
    source = source_skills(repo)
    skills_dir, agents_path = destinations(args)
    removed = []
    if skills_dir.is_dir():
        for entry in sorted(skills_dir.iterdir()):
            expected = (source / entry.name).resolve()
            if entry.is_symlink() and link_target(entry) == expected:
                entry.unlink()
                removed.append(entry.name)
    agents_removed = remove_block(agents_path)
    return {
        "command": "remove",
        "scope": args.scope,
        "skills": str(skills_dir),
        "removed": len(removed),
        "agents_md": str(agents_path),
        "agents_md_removed": agents_removed,
        "changed": bool(removed) or agents_removed,
    }


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--scope",
        choices=("global", "project"),
        default="global",
        help="install user-wide or into the current project (default: global)",
    )
    common.add_argument(
        "--repo",
        default=None,
        help="repository root to install from (default: this checkout)",
    )
    common.add_argument("--json", action="store_true", help="machine-readable output")
    parser = argparse.ArgumentParser(
        prog="install_deepseek_harness",
        parents=[common],
        description="Install Clanker Skills for DeepSeek Harness.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install", parents=[common], help="link skills and update AGENTS.md")
    sub.add_parser("status", parents=[common], help="report links and the managed block")
    sub.add_parser("remove", parents=[common], help="remove links and the managed block")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    repo = repo_root(args.repo)
    commands = {"install": install, "status": status, "remove": remove}
    try:
        result = commands[args.command](args, repo)
    except (OSError, SystemExit) as exc:
        print(f"install_deepseek_harness: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
