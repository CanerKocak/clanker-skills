#!/usr/bin/env python3
"""Tests for install_deepseek_harness.py. Isolated temp repository and home."""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import install_deepseek_harness as installer


class InstallerCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = os.path.join(self.tmp.name, "repo")
        self.home = os.path.join(self.tmp.name, "home")
        os.makedirs(self.home)
        self.write(
            "AGENTS.md",
            "# Clanker output contract\n\n## Default to tables\n\nUse a table.\n",
        )
        fence = chr(96) * 3
        self.write(
            "docs/global-routing.md",
            "# Global skill routing\n\n"
            + fence
            + "markdown\n## Clanker skill routing\n\nUse $writing-plans.\n"
            + fence
            + "\n",
        )
        for name in ("writing-plans", "simple-english"):
            self.write(
                f"plugins/clanker-skills/skills/{name}/SKILL.md",
                f"---\nname: {name}\ndescription: test skill\n---\n\nBody.\n",
            )
        self.env = mock.patch.dict(
            os.environ, {"DSH_HOME": os.path.join(self.home, ".dsh")}
        )
        self.env.start()
        self.addCleanup(self.env.stop)

    def write(self, relative, text):
        path = os.path.join(self.repo, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def invoke(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            code = installer.main([*argv, "--repo", self.repo, "--json"])
        return code, json.loads(out.getvalue())

    def dsh(self, *parts):
        return os.path.join(self.home, ".dsh", *parts)

    def test_install_links_skills_and_writes_contract(self):
        code, result = self.invoke("install")
        self.assertEqual(code, 0)
        self.assertEqual(result["installed"], 2)
        for name in ("writing-plans", "simple-english"):
            link = self.dsh("skills", name)
            self.assertTrue(os.path.islink(link))
            self.assertEqual(
                os.path.realpath(link),
                os.path.realpath(
                    os.path.join(
                        self.repo, "plugins", "clanker-skills", "skills", name
                    )
                ),
            )
        with open(self.dsh("AGENTS.md"), encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("# Clanker output contract", text)
        self.assertIn("## Clanker skill routing", text)
        self.assertIn("$writing-plans", text)

    def test_install_is_idempotent(self):
        self.invoke("install")
        code, result = self.invoke("install")
        self.assertEqual(code, 0)
        self.assertFalse(result["changed"])
        self.assertEqual(result["installed"], 0)
        self.assertEqual(result["unchanged"], 2)

    def test_status_reports_wiring(self):
        self.invoke("install")
        code, status = self.invoke("status")
        self.assertEqual(code, 0)
        self.assertTrue(status["wired"])
        self.assertEqual(status["linked"], 2)
        self.assertTrue(status["agents_md_installed"])

    def test_remove_unlinks_and_strips_block(self):
        self.invoke("install")
        code, result = self.invoke("remove")
        self.assertEqual(code, 0)
        self.assertEqual(result["removed"], 2)
        self.assertTrue(result["agents_md_removed"])
        self.assertFalse(os.path.exists(self.dsh("skills", "writing-plans")))
        self.assertFalse(os.path.exists(self.dsh("AGENTS.md")))

    def test_install_preserves_existing_content(self):
        custom = self.dsh("skills", "custom")
        os.makedirs(custom)
        self.write("AGENTS.md", "# Clanker output contract\n\nUse a table.\n")
        with open(self.dsh("AGENTS.md"), "w", encoding="utf-8") as handle:
            handle.write("Keep this project note.\n")
        self.invoke("install")
        with open(self.dsh("AGENTS.md"), encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("Keep this project note.", text)
        self.assertIn("# Clanker output contract", text)
        self.assertTrue(os.path.isdir(custom))
        self.invoke("remove")
        with open(self.dsh("AGENTS.md"), encoding="utf-8") as handle:
            text = handle.read()
        self.assertEqual(text, "Keep this project note.\n")
        self.assertTrue(os.path.isdir(custom))

    def test_project_scope_targets_the_project(self):
        project = os.path.join(self.tmp.name, "project")
        os.makedirs(project)
        cwd = os.getcwd()
        os.chdir(project)
        self.addCleanup(os.chdir, cwd)
        code, result = self.invoke("install", "--scope", "project")
        self.assertEqual(code, 0)
        self.assertEqual(result["scope"], "project")
        skill = os.path.join(project, ".dsh", "skills", "writing-plans")
        self.assertTrue(os.path.islink(skill))
        with open(os.path.join(project, "AGENTS.md"), encoding="utf-8") as handle:
            self.assertIn("## Clanker skill routing", handle.read())
        self.assertFalse(os.path.exists(self.dsh("skills")))
        self.invoke("remove", "--scope", "project")
        self.assertFalse(os.path.exists(skill))
        self.assertFalse(os.path.exists(os.path.join(project, "AGENTS.md")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
