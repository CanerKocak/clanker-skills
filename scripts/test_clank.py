#!/usr/bin/env python3
"""Tests for clank.py. Isolated: temp HOME, local git repos, PATH stubs."""

import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import clank

GIT_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@t",
    "GIT_CONFIG_NOSYSTEM": "1",
}


def git(*args, cwd=None, env_extra=None):
    env = dict(os.environ, **GIT_ENV, **(env_extra or {}))
    proc = subprocess.run(["git", *args], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


class ClankCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = os.path.join(self.tmp.name, "home")
        self.work = os.path.join(self.tmp.name, "work")
        os.makedirs(self.home)
        os.makedirs(self.work)
        # origin repo with a main branch
        self.origin = os.path.join(self.tmp.name, "origin")
        os.makedirs(self.origin)
        git("init", "-b", "main", cwd=self.origin)
        git("commit", "--allow-empty", "-m", "seed", cwd=self.origin)
        self.env = {"HOME": self.home, "CLANK_REPO": self.origin, "CLANK_REF": "main",
                    "CLANK_DIR": os.path.join(self.work, "clanker-skills")}
        self.env_patch = mock.patch.dict(os.environ, self.env)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def invoke(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            code = clank.main(list(argv))
        return code, out.getvalue()

    def clone(self):
        return os.path.join(self.work, "clanker-skills")

    def test_opencode_global_wire_preserves_other_keys(self):
        config = os.path.join(self.home, ".config", "opencode", "opencode.json")
        os.makedirs(os.path.dirname(config))
        with open(config, "w") as handle:
            json.dump({"model": "m", "skills": {"paths": ["/other"]}}, handle)
        code, _ = self.invoke("install", "--harness", "opencode", "--json")
        self.assertEqual(code, 0)
        with open(config) as handle:
            data = json.load(handle)
        self.assertEqual(data["model"], "m")
        self.assertIn("/other", data["skills"]["paths"])
        want = os.path.join(self.clone(), "platforms", "opencode", ".opencode", "skills")
        self.assertIn(want, data["skills"]["paths"])
        # idempotent
        code, raw = self.invoke("install", "--harness", "opencode", "--json")
        self.assertEqual(code, 0)
        self.assertFalse(json.loads(raw)["harnesses"][0]["changed"])

    def test_opencode_project_scope(self):
        project = os.path.join(self.work, "proj")
        os.makedirs(project)
        cwd = os.getcwd()
        os.chdir(project)
        self.addCleanup(os.chdir, cwd)
        code, _ = self.invoke("install", "--harness", "opencode", "--scope", "project")
        self.assertEqual(code, 0)
        with open(os.path.join(project, "opencode.json")) as handle:
            data = json.load(handle)
        self.assertTrue(data["skills"]["paths"])

    def test_pi_roundtrip(self):
        code, _ = self.invoke("install", "--harness", "pi", "--json")
        self.assertEqual(code, 0)
        config = os.path.join(self.home, ".pi", "agent", "settings.json")
        with open(config) as handle:
            self.assertEqual(len(json.load(handle)["skills"]), 1)
        code, raw = self.invoke("remove", "--harness", "pi", "--json")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(raw)["harnesses"][0]["changed"])
        with open(config) as handle:
            self.assertEqual(json.load(handle)["skills"], [])

    def test_grok_creates_extends_unwires(self):
        config = os.path.join(self.home, ".grok", "config.toml")
        code, _ = self.invoke("install", "--harness", "grok")
        self.assertEqual(code, 0)
        with open(config) as handle:
            text = handle.read()
        self.assertIn('[skills]', text)
        want = os.path.join(self.clone(), "platforms", "grok", ".grok", "skills")
        self.assertIn(want, text)
        # existing config with another table keeps its content
        with open(config, "w") as handle:
            handle.write('[other]\nkey = 1\n\n[skills]\npaths = ["/keep"]\n')
        code, _ = self.invoke("install", "--harness", "grok")
        self.assertEqual(code, 0)
        with open(config) as handle:
            text = handle.read()
        self.assertIn('[other]\nkey = 1', text)
        self.assertIn('"/keep"', text)
        self.assertIn(want, text)
        code, _ = self.invoke("remove", "--harness", "grok")
        self.assertEqual(code, 0)
        with open(config) as handle:
            text = handle.read()
        self.assertIn('"/keep"', text)
        self.assertNotIn(want, text)

    def test_update_fast_forward_and_dirty_refusal(self):
        code, _ = self.invoke("install", "--harness", "opencode")
        self.assertEqual(code, 0)
        git("commit", "--allow-empty", "-m", "second", cwd=self.origin)
        code, raw = self.invoke("update", "--json")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(raw)["updated"])
        # dirty tree refuses
        with open(os.path.join(self.clone(), "dirty.txt"), "w") as handle:
            handle.write("x")
        code, raw = self.invoke("update", "--json")
        self.assertEqual(code, 1)
        self.assertIn("dirty", json.loads(raw)["error"])

    def test_remove_purge(self):
        self.invoke("install", "--harness", "opencode")
        code, raw = self.invoke("remove", "--harness", "opencode", "--purge", "--json")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(raw)["purged"])
        self.assertFalse(os.path.exists(self.clone()))
        # dirty clone refuses purge without --force
        self.invoke("install", "--harness", "opencode")
        with open(os.path.join(self.clone(), "dirty.txt"), "w") as handle:
            handle.write("x")
        code, _ = self.invoke("remove", "--harness", "opencode", "--purge")
        self.assertEqual(code, 1)
        self.assertTrue(os.path.isdir(self.clone()))
        code, _ = self.invoke("remove", "--harness", "opencode", "--purge", "--force")
        self.assertEqual(code, 0)
        self.assertFalse(os.path.exists(self.clone()))

    def test_claude_prints_manual_step(self):
        code, raw = self.invoke("install", "--harness", "claude-code", "--json")
        self.assertEqual(code, 0)
        step = json.loads(raw)["harnesses"][0]
        self.assertIn("--plugin-dir", step["manual_step"])

    def test_codex_stub_and_missing(self):
        bindir = os.path.join(self.tmp.name, "bin")
        os.makedirs(bindir)
        log = os.path.join(self.tmp.name, "codex.log")
        with open(os.path.join(bindir, "codex"), "w") as handle:
            handle.write(f"#!/bin/sh\necho \"$@\" >> {log}\n")
        os.chmod(os.path.join(bindir, "codex"), os.stat(os.path.join(bindir, "codex")).st_mode | stat.S_IEXEC)
        with mock.patch.dict(os.environ, {"PATH": bindir + os.pathsep + os.environ["PATH"]}):
            code, raw = self.invoke("install", "--harness", "codex", "--json")
        self.assertEqual(code, 0)
        with open(log) as handle:
            self.assertIn("marketplace add", handle.read())
        # without the binary it prints the step instead
        with mock.patch.dict(os.environ, {"PATH": bindir}):
            with mock.patch("shutil.which", return_value=None):
                code, raw = self.invoke("install", "--harness", "codex", "--json")
        self.assertEqual(code, 0)
        self.assertIn("marketplace add", json.loads(raw)["harnesses"][0]["manual_step"])

    def test_status_reports(self):
        code, raw = self.invoke("status", "--json")
        self.assertEqual(code, 0)
        self.assertFalse(json.loads(raw)["clone"])
        self.invoke("install", "--harness", "opencode,pi")
        code, raw = self.invoke("status", "--harness", "opencode,pi", "--json")
        state = json.loads(raw)
        self.assertTrue(state["clone"])
        self.assertFalse(state["dirty"])
        self.assertTrue(all(h["wired"] for h in state["harnesses"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
