"""Tests for hooks/rules_check.py on throwaway git repositories."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "hooks", "rules_check.py")
spec = importlib.util.spec_from_file_location("rules_check", SCRIPT)
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)

SYNC = """\
# comment
api:
  paths:
    - "src/routes/**"
  generate: ""
database:
  paths:
    - "migrations/**"
architecture:
  paths:
    - "docker-compose*.yml"
"""


class Repo:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "test")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *args):
        return subprocess.run(["git", "-C", self.root, *args], check=True,
                              capture_output=True, text=True).stdout

    def write(self, rel, text="x\n"):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def commit(self, message="change", *paths):
        self.git("add", "-A", *paths)
        self.git("commit", "-q", "-m", message)

    def run(self, *args, stdin=None):
        return subprocess.run([sys.executable, SCRIPT, *args], cwd=self.root,
                              input=stdin, capture_output=True, text=True)


class ParseTest(unittest.TestCase):
    def test_flat_subset(self):
        data = rc.parse_sync(SYNC)
        self.assertEqual(data["api"]["paths"], ["src/routes/**"])
        self.assertEqual(data["api"]["generate"], "")
        self.assertEqual(data["database"]["paths"], ["migrations/**"])

    def test_globs(self):
        self.assertTrue(rc.matches("src/routes/a/b.py", ["src/routes/**"]))
        self.assertTrue(rc.matches("docker-compose.prod.yml", ["docker-compose*.yml"]))
        self.assertFalse(rc.matches("src/other.py", ["src/routes/**"]))
        self.assertTrue(rc.matches("a/b/c.sql", ["**/*.sql"]))
        self.assertTrue(rc.matches("c.sql", ["**/*.sql"]))

    def test_skip_trailer(self):
        msg = "fix\n\nRules-Skip: api, database — internal refactor\n"
        self.assertEqual(rc.skipped_sections(msg), {"api", "database"})

    def test_git_commit_detection(self):
        self.assertTrue(rc.is_git_commit('git add a && git commit -m "x"'))
        self.assertTrue(rc.is_git_commit("git -C /tmp/r commit -q -m x"))
        self.assertFalse(rc.is_git_commit("git log --grep commit"))


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.repo.write("rules/sync.yml", SYNC)
        self.repo.write("rules/database/erd.md")
        self.repo.commit("init")

    def tearDown(self):
        self.repo.tmp.cleanup()

    def test_drift_detected_in_staged(self):
        self.repo.write("migrations/001.sql")
        self.repo.git("add", "-A")
        res = self.repo.run("--staged")
        self.assertEqual(res.returncode, 1)
        self.assertIn("database code changed (migrations/001.sql)", res.stdout)

    def test_schema_updated_is_fine(self):
        self.repo.write("migrations/001.sql")
        self.repo.write("rules/database/erd.md", "updated\n")
        self.repo.git("add", "-A")
        self.assertEqual(self.repo.run("--staged").returncode, 0)

    def test_range_with_skip_trailer(self):
        base = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.write("src/routes/users.py")
        self.repo.commit("refactor\n\nRules-Skip: api — no contract change")
        self.assertEqual(self.repo.run("--range", f"{base}..HEAD").returncode, 0)

    def test_range_without_skip_fails(self):
        base = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.write("docker-compose.yml")
        self.repo.commit("add redis")
        res = self.repo.run("--range", f"{base}..HEAD")
        self.assertEqual(res.returncode, 1)
        self.assertIn("architecture", res.stdout)

    def test_monorepo_paths_are_relative_to_service(self):
        self.repo.write("services/billing/rules/sync.yml", SYNC)
        self.repo.commit("add service")
        self.repo.write("services/billing/migrations/001.sql")
        self.repo.git("add", "-A")
        res = self.repo.run("--staged")
        self.assertEqual(res.returncode, 1)
        self.assertIn("services/billing/rules/database/", res.stdout)

    def test_hook_warns_after_commit(self):
        self.repo.write("migrations/002.sql")
        self.repo.commit("add table")
        payload = json.dumps({"tool_name": "Bash", "cwd": self.repo.root,
                              "tool_input": {"command": 'git commit -m "add table"'}})
        res = self.repo.run("--hook", stdin=payload)
        self.assertEqual(res.returncode, 0)
        ctx = json.loads(res.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("rules/database/", ctx)

    def test_hook_silent_for_other_commands(self):
        payload = json.dumps({"tool_name": "Bash", "cwd": self.repo.root,
                              "tool_input": {"command": "ls"}})
        res = self.repo.run("--hook", stdin=payload)
        self.assertEqual((res.returncode, res.stdout), (0, ""))

    def test_hook_silent_without_sync_file(self):
        other = Repo()
        try:
            other.write("migrations/001.sql")
            other.commit("init")
            payload = json.dumps({"tool_name": "Bash", "cwd": other.root,
                                  "tool_input": {"command": "git commit -m x"}})
            res = other.run("--hook", stdin=payload)
            self.assertEqual((res.returncode, res.stdout), (0, ""))
        finally:
            other.tmp.cleanup()


class VerifyGeneratedTest(unittest.TestCase):
    def test_out_of_date_contract(self):
        repo = Repo()
        try:
            repo.write("rules/sync.yml", SYNC.replace('generate: ""', 'generate: "echo v2 > rules/api/openapi.yaml"'))
            repo.write("rules/api/openapi.yaml", "v1\n")
            repo.commit("init")
            res = repo.run("--verify-generated")
            self.assertEqual(res.returncode, 1)
            self.assertIn("out of date", res.stdout)
        finally:
            repo.tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
