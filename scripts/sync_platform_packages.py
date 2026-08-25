#!/usr/bin/env python3
"""Generate or verify standalone skill trees for supported agent runtimes."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SKILLS = ROOT / "plugins" / "clanker-skills" / "skills"
PLATFORM_SKILL_ROOTS = {
    "claude-code": ROOT / "platforms" / "claude-code" / "skills",
    "opencode": ROOT / "platforms" / "opencode" / ".opencode" / "skills",
    "pi": ROOT / "platforms" / "pi" / "skills",
    "grok": ROOT / "platforms" / "grok" / ".grok" / "skills",
}
EXCLUDED_PARTS = {"agents"}


def skill_directories(root: Path) -> list[Path]:
    """Return direct skill folders with a canonical entrypoint."""
    if not root.is_dir():
        raise ValueError(f"missing skills directory: {root.relative_to(ROOT)}")
    return sorted(
        (path for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()),
        key=lambda path: path.name,
    )


def portable_files(skill_directory: Path) -> dict[Path, bytes]:
    """Read every portable package file, excluding Codex-only UI metadata."""
    files: dict[Path, bytes] = {}
    for path in sorted(skill_directory.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(skill_directory)
        if EXCLUDED_PARTS.intersection(relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"portable source must not contain symlinks: {path.relative_to(ROOT)}")
        files[relative] = path.read_bytes()
    return files


def file_digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def compare_tree(source: Path, destination: Path) -> list[str]:
    """Return exact file-tree differences between one source and one mirror."""
    source_files = portable_files(source)
    if not destination.is_dir():
        return [f"missing mirror directory: {destination.relative_to(ROOT)}"]

    destination_files: dict[Path, bytes] = {}
    for path in sorted(destination.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(destination)
        if path.is_symlink():
            return [f"mirror must not contain symlinks: {path.relative_to(ROOT)}"]
        destination_files[relative] = path.read_bytes()

    errors: list[str] = []
    missing = sorted(set(source_files) - set(destination_files))
    extra = sorted(set(destination_files) - set(source_files))
    for relative in missing:
        errors.append(f"missing mirrored file: {destination.relative_to(ROOT) / relative}")
    for relative in extra:
        errors.append(f"unexpected mirrored file: {destination.relative_to(ROOT) / relative}")
    for relative in sorted(set(source_files).intersection(destination_files)):
        if source_files[relative] != destination_files[relative]:
            errors.append(
                "stale mirrored file: "
                f"{destination.relative_to(ROOT) / relative} "
                f"({file_digest(destination_files[relative])[:12]} != "
                f"{file_digest(source_files[relative])[:12]})"
            )
    return errors


def check() -> list[str]:
    """Verify every native runtime tree mirrors the portable source exactly."""
    source_directories = skill_directories(SOURCE_SKILLS)
    source_names = [directory.name for directory in source_directories]
    errors: list[str] = []
    for platform, target_root in PLATFORM_SKILL_ROOTS.items():
        try:
            target_directories = skill_directories(target_root)
        except ValueError as exc:
            errors.append(f"{platform}: {exc}")
            continue
        target_names = [directory.name for directory in target_directories]
        if target_names != source_names:
            errors.append(
                f"{platform}: skill directory inventory mismatch; "
                f"expected={source_names}, actual={target_names}"
            )
            continue
        for source in source_directories:
            errors.extend(compare_tree(source, target_root / source.name))
    return errors


def sync() -> None:
    """Replace each generated skill tree with a portable source mirror."""
    source_directories = skill_directories(SOURCE_SKILLS)
    generated_root = (ROOT / "platforms").resolve()
    for target_root in PLATFORM_SKILL_ROOTS.values():
        resolved_target = target_root.resolve()
        try:
            resolved_target.relative_to(generated_root)
        except ValueError as exc:
            raise ValueError(f"refusing to replace non-platform path: {target_root}") from exc
        if target_root.exists():
            shutil.rmtree(target_root)
        target_root.mkdir(parents=True, exist_ok=True)
        for source in source_directories:
            destination = target_root / source.name
            for relative, payload in portable_files(source).items():
                target = destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
                shutil.copymode(source / relative, target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify generated platform packages without changing files",
    )
    args = parser.parse_args()

    try:
        if args.check:
            errors = check()
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            count = len(skill_directories(SOURCE_SKILLS))
            print(f"Verified {count} skills across {len(PLATFORM_SKILL_ROOTS)} platform packages.")
            return 0

        sync()
        errors = check()
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    count = len(skill_directories(SOURCE_SKILLS))
    print(f"Synchronized {count} skills across {len(PLATFORM_SKILL_ROOTS)} platform packages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
