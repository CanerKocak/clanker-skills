#!/usr/bin/env python3
"""Validate the Clanker Skills plugin without third-party dependencies."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "clanker-skills"
SKILLS = PLUGIN / "skills"
EXPECTED_SKILLS = (
    "adaptive-code-orchestrator",
    "analyze-data-quality",
    "ast-grep-callchain-audit",
    "call-chain-invariants",
    "differential-review",
    "edit-the-chain",
    "gather-business-context",
    "pdf-findings-schema",
    "pdf-security-audit-report",
    "pdf-typst-report",
    "pdf-visual-qa",
    "prompt-leakage",
    "semantic-blast-radius",
    "thermo-nuclear-code-quality-review",
    "uncodixfy",
    "yagni-anti-ceremonial",
)
UNCODIXFY_UPSTREAM_BLOBS = {
    "LICENSE": "19ebb1bd6d27897b0995b635e7634969f3e9e512",
    "README.md": "5948d8b70bc4e595b304c0c17c7a4d6463f2cb45",
    "SKILL.md": "c4fdb52f992fce4bd3de92df6e336e3a861e9835",
    "Uncodixfy.md": "6d9c67a3c3aafbfb36eab4961c7fb8953f6953e2",
    "images/1.png": "4872fd8896e626ded9615f7e8d71ca38453aaa51",
    "images/2.png": "bfaf808ea0cbabe49adc4d1885ff03df5a501d88",
    "images/3.png": "c4a4fbb910c30e283322718e06051e962b2319b6",
    "images/4.png": "8ad923298a6116771da14fedf682450cf1f9a0ed",
    "images/thumb.jpg": "c95fc759edde030f9a1f16eaa45369c8388cf44a",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_REFERENCE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
HTML_LINK = re.compile(r"(?:href|src)=[\"']([^\"']+)[\"']", re.IGNORECASE)


def yaml_scalar(text: str, key: str) -> str | None:
    """Read one scalar from the small YAML subset used by skill metadata."""
    lines = text.splitlines()
    pattern = re.compile(rf"^\s*{re.escape(key)}:\s*(.*)$")
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match:
            continue
        value = match.group(1).strip()
        if value in {">", ">-", "|", "|-"}:
            parts: list[str] = []
            for following in lines[index + 1 :]:
                if following and not following[0].isspace():
                    break
                if following.strip():
                    parts.append(following.strip())
            return " ".join(parts)
        if value.startswith(("'", '"')):
            try:
                parsed = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                return None
            return parsed if isinstance(parsed, str) else None
        return value or None
    return None


def frontmatter(document: Path, errors: list[str]) -> str:
    text = document.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        errors.append(f"{document.relative_to(ROOT)}: missing opening frontmatter fence")
        return ""
    try:
        closing = lines.index("---", 1)
    except ValueError:
        errors.append(f"{document.relative_to(ROOT)}: missing closing frontmatter fence")
        return ""
    return "\n".join(lines[1:closing])


def validate_inventory(errors: list[str]) -> None:
    expected_paths = tuple(
        f"plugins/clanker-skills/skills/{name}/SKILL.md" for name in EXPECTED_SKILLS
    )
    discovered_paths = tuple(
        sorted(
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("SKILL.md")
            if ".git" not in path.parts
        )
    )
    if discovered_paths != expected_paths:
        missing_paths = sorted(set(expected_paths) - set(discovered_paths))
        noncanonical_paths = sorted(set(discovered_paths) - set(expected_paths))
        errors.append(
            "canonical skill paths mismatch; "
            f"missing={missing_paths}, noncanonical={noncanonical_paths}"
        )

    discovered = tuple(
        sorted(path.parent.name for path in SKILLS.glob("*/SKILL.md") if path.is_file())
    )
    if discovered != EXPECTED_SKILLS:
        missing = sorted(set(EXPECTED_SKILLS) - set(discovered))
        unexpected = sorted(set(discovered) - set(EXPECTED_SKILLS))
        errors.append(f"skill inventory mismatch; missing={missing}, unexpected={unexpected}")


def validate_skills(errors: list[str]) -> None:
    for skill_name in EXPECTED_SKILLS:
        skill_dir = SKILLS / skill_name
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"{skill_file.relative_to(ROOT)}: missing")
            continue

        metadata = frontmatter(skill_file, errors)
        declared_name = yaml_scalar(metadata, "name")
        description = yaml_scalar(metadata, "description")
        if declared_name != skill_name:
            errors.append(
                f"{skill_file.relative_to(ROOT)}: name {declared_name!r} does not match directory"
            )
        if not declared_name or not NAME_PATTERN.fullmatch(declared_name):
            errors.append(f"{skill_file.relative_to(ROOT)}: invalid skill name")
        if not description:
            errors.append(f"{skill_file.relative_to(ROOT)}: missing description")

        ui_file = skill_dir / "agents" / "openai.yaml"
        if not ui_file.is_file():
            errors.append(f"{ui_file.relative_to(ROOT)}: missing")
            continue
        ui = ui_file.read_text(encoding="utf-8")
        display_name = yaml_scalar(ui, "display_name")
        short_description = yaml_scalar(ui, "short_description")
        brand_color = yaml_scalar(ui, "brand_color")
        default_prompt = yaml_scalar(ui, "default_prompt")
        if not display_name:
            errors.append(f"{ui_file.relative_to(ROOT)}: missing display_name")
        if not short_description or not 25 <= len(short_description) <= 64:
            length = len(short_description or "")
            errors.append(
                f"{ui_file.relative_to(ROOT)}: short_description length is {length}, "
                "expected 25-64"
            )
        if brand_color != "#D7FF64":
            errors.append(f"{ui_file.relative_to(ROOT)}: brand_color must be #D7FF64")
        if not default_prompt or f"${skill_name}" not in default_prompt:
            errors.append(
                f"{ui_file.relative_to(ROOT)}: default_prompt must mention ${skill_name}"
            )


def validate_plugin(errors: list[str]) -> None:
    manifest_path = PLUGIN / ".codex-plugin" / "plugin.json"
    marketplace_path = ROOT / ".agents" / "plugins" / "marketplace.json"
    for path in (manifest_path, marketplace_path):
        if not path.is_file():
            errors.append(f"{path.relative_to(ROOT)}: missing")
            return

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON: {exc}")
        return

    if not isinstance(manifest, dict):
        errors.append("plugin manifest must be a JSON object")
        return
    if not isinstance(marketplace, dict):
        errors.append("marketplace must be a JSON object")
        return

    if manifest.get("name") != "clanker-skills":
        errors.append("plugin name must be clanker-skills")
    if manifest.get("skills") != "./skills/":
        errors.append("plugin skills path must be ./skills/")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", ""))):
        errors.append("plugin version must use semantic versioning")
    for field in ("description", "homepage", "repository"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            errors.append(f"plugin {field} must be a non-empty string")
    for field in ("homepage", "repository"):
        value = manifest.get(field)
        if isinstance(value, str) and not value.startswith("https://"):
            errors.append(f"plugin {field} must use https")
    author = manifest.get("author")
    if not isinstance(author, dict) or not isinstance(author.get("name"), str):
        errors.append("plugin author.name must be present")
    elif not isinstance(author.get("url"), str) or not author["url"].startswith("https://"):
        errors.append("plugin author.url must use https")
    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append("plugin interface must be an object")
    else:
        for field in (
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
            "brandColor",
        ):
            if not isinstance(interface.get(field), str) or not interface[field].strip():
                errors.append(f"plugin interface.{field} must be a non-empty string")
        prompts = interface.get("defaultPrompt")
        if not isinstance(prompts, list) or not prompts or not all(
            isinstance(prompt, str) and prompt.strip() for prompt in prompts
        ):
            errors.append("plugin interface.defaultPrompt must contain prompts")
        if interface.get("brandColor") != "#D7FF64":
            errors.append("plugin interface.brandColor must be #D7FF64")
        if not isinstance(interface.get("capabilities"), list):
            errors.append("plugin interface.capabilities must be an array")

    if marketplace.get("name") != "clanker-skills":
        errors.append("marketplace name must be clanker-skills")
    marketplace_interface = marketplace.get("interface")
    if not isinstance(marketplace_interface, dict) or marketplace_interface.get(
        "displayName"
    ) != "Clanker Skills":
        errors.append("marketplace displayName must be Clanker Skills")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        errors.append("marketplace plugins must be an array")
        return
    matching = [
        entry
        for entry in plugins
        if isinstance(entry, dict) and entry.get("name") == "clanker-skills"
    ]
    if len(matching) != 1:
        errors.append("marketplace must contain exactly one clanker-skills entry")
    else:
        entry = matching[0]
        if entry.get("source") != {
            "source": "local",
            "path": "./plugins/clanker-skills",
        }:
            errors.append("marketplace source must point to ./plugins/clanker-skills")
        if entry.get("policy") != {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        }:
            errors.append("marketplace policy must use the reviewed defaults")
        if entry.get("category") != "Developer Tools":
            errors.append("marketplace category must be Developer Tools")


def validate_catalog_surfaces(errors: list[str]) -> None:
    readme_path = ROOT / "README.md"
    routing_path = ROOT / "docs" / "global-routing.md"
    manifest_path = PLUGIN / ".codex-plugin" / "plugin.json"
    required_paths = (readme_path, routing_path, manifest_path)
    missing_paths = [path for path in required_paths if not path.is_file()]
    for path in missing_paths:
        errors.append(f"{path.relative_to(ROOT)}: missing catalog surface")
    if missing_paths:
        return

    readme = readme_path.read_text(encoding="utf-8")
    routing = routing_path.read_text(encoding="utf-8")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    skill_count = len(EXPECTED_SKILLS)
    for skill_name in EXPECTED_SKILLS:
        catalog_target = f"plugins/clanker-skills/skills/{skill_name}/SKILL.md"
        if readme.count(f"]({catalog_target})") != 1:
            errors.append(
                f"README.md: expected one catalog link for {skill_name}"
            )
        if routing.count(f"${skill_name}") != 1:
            errors.append(
                f"docs/global-routing.md: expected one routing entry for ${skill_name}"
            )

    if f"Its {skill_count} agent skills" not in readme:
        errors.append("README.md: introductory skill count is stale")
    if f"skills-{skill_count}-" not in readme:
        errors.append("README.md: skill-count badge is stale")
    interface = manifest.get("interface") if isinstance(manifest, dict) else None
    long_description = interface.get("longDescription", "") if isinstance(interface, dict) else ""
    if f"of {skill_count} Codex skills" not in long_description:
        errors.append("plugin longDescription skill count is stale")


def markdown_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    return unquote(target)


def validate_local_target(document: Path, raw_target: str, errors: list[str]) -> None:
    target = markdown_target(raw_target)
    if not target or target.startswith(
        ("#", "http://", "https://", "mailto:", "data:")
    ):
        return
    target = target.split("#", 1)[0].split("?", 1)[0]
    resolved = (document.parent / target).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError:
        errors.append(
            f"{document.relative_to(ROOT)}: local link escapes the repository {raw_target!r}"
        )
        return
    if not resolved.exists():
        errors.append(
            f"{document.relative_to(ROOT)}: broken local link {raw_target!r}"
        )


def validate_links(errors: list[str]) -> None:
    for document in sorted(ROOT.rglob("*.md")):
        if ".git" in document.parts:
            continue
        text = document.read_text(encoding="utf-8")
        matches = (
            *MARKDOWN_LINK.findall(text),
            *MARKDOWN_REFERENCE.findall(text),
            *HTML_LINK.findall(text),
        )
        for target in dict.fromkeys(matches):
            validate_local_target(document, target, errors)


def validate_provenance(errors: list[str]) -> None:
    uncodixfy_path = SKILLS / "uncodixfy"
    license_path = uncodixfy_path / "LICENSE"
    notices_path = ROOT / "THIRD_PARTY_NOTICES.md"
    if not license_path.is_file():
        errors.append(f"{license_path.relative_to(ROOT)}: missing upstream license")
    else:
        license_text = license_path.read_text(encoding="utf-8")
        if "MIT License" not in license_text or "Copyright (c) 2026 cyxzdev" not in license_text:
            errors.append(f"{license_path.relative_to(ROOT)}: unexpected license content")
    for relative_path, expected_blob in UNCODIXFY_UPSTREAM_BLOBS.items():
        source_path = uncodixfy_path / relative_path
        if not source_path.is_file():
            errors.append(f"{source_path.relative_to(ROOT)}: missing upstream payload")
            continue
        payload = source_path.read_bytes()
        header = f"blob {len(payload)}\0".encode()
        actual_blob = hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()
        if actual_blob != expected_blob:
            errors.append(
                f"{source_path.relative_to(ROOT)}: upstream blob changed; "
                "update provenance before publishing"
            )
    if not notices_path.is_file():
        errors.append("THIRD_PARTY_NOTICES.md: missing")
    else:
        notices = notices_path.read_text(encoding="utf-8")
        required = (
            "plugins/clanker-skills/skills/uncodixfy",
            "https://github.com/cyxzdev/Uncodixfy",
            "e0e028058b5259debdd94b78147c6d6c77bf7da2",
            "MIT License",
        )
        for value in required:
            if value not in notices:
                errors.append(f"THIRD_PARTY_NOTICES.md: missing {value!r}")


def validate_social_preview(errors: list[str]) -> None:
    preview_path = ROOT / ".github" / "assets" / "social-preview.png"
    if not preview_path.is_file():
        errors.append(f"{preview_path.relative_to(ROOT)}: missing")
        return
    data = preview_path.read_bytes()
    if len(data) >= 1_000_000:
        errors.append(f"{preview_path.relative_to(ROOT)}: must remain under 1 MB")
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        errors.append(f"{preview_path.relative_to(ROOT)}: invalid PNG header")
        return
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1280, 640):
        errors.append(
            f"{preview_path.relative_to(ROOT)}: expected 1280x640, found {width}x{height}"
        )


def main() -> int:
    errors: list[str] = []
    validate_inventory(errors)
    validate_skills(errors)
    validate_plugin(errors)
    validate_catalog_surfaces(errors)
    validate_links(errors)
    validate_provenance(errors)
    validate_social_preview(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(
        f"Validated {len(EXPECTED_SKILLS)} skills, plugin metadata, local links, "
        "provenance, and the social preview."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
