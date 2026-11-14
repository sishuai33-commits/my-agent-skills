"""Isolated fake git/curl: no real repository refs or network are touched."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/skills-check.sh"
PAYLOAD = b'---\nname: fixture\nmetadata:\n  version: "2.6"\n---\nnew content\n'
FAKE = r'''
import os, sys
from pathlib import Path
name = Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ["FAKE_LOG"], "a") as log:
    log.write(name + " " + " ".join(args[:5]) + "\n")
if name == "curl":
    if os.environ.get("FAKE_CURL_FAIL"): sys.exit(22)
    Path(args[args.index("-o") + 1]).write_bytes(
        b"" if os.environ.get("FAKE_CURL_EMPTY") else Path(os.environ["FAKE_PAYLOAD"]).read_bytes())
    sys.exit(0)
path = Path(args[1])
cmd = args[2:]
if cmd == ["rev-parse", "--show-toplevel"]:
    if path.name.startswith("doc"): sys.exit(128)
    print(os.environ["FAKE_REPO"])
elif cmd == ["rev-parse", "--abbrev-ref", "HEAD"]: print("main")
elif cmd == ["status", "--porcelain"]: pass
elif cmd == ["remote"]:
    if not os.environ.get("FAKE_LOCAL"): print("origin")
elif cmd[:1] == ["fetch"]:
    sys.exit(128 if os.environ.get("FAKE_FETCH_FAIL") else 0)
elif cmd[:2] == ["rev-parse", "--verify"]:
    sys.exit(1 if os.environ.get("FAKE_NO_BRANCH") else 0)
elif cmd[:1] == ["rev-list"]:
    print(os.environ.get("FAKE_BEHIND", "0") + "\t0")
else:
    sys.exit(90)
'''


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="skills-check-offline-")
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.root = root / "skills"
        self.root.mkdir()
        bin_dir = root / "bin"
        bin_dir.mkdir()
        for command in ["git", "curl"]:
            exe = bin_dir / command
            exe.write_text(f"#!{sys.executable}\n" + FAKE)
            exe.chmod(0o700)
        payload = root / "payload.md"
        payload.write_bytes(PAYLOAD)
        self.log = root / "calls.log"
        self.env = {**os.environ, "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
                    "SKILLS_ROOTS": str(self.root), "FAKE_LOG": str(self.log),
                    "FAKE_PAYLOAD": str(payload), "FAKE_REPO": str(root / "repo")}

    def skill(self, name="git-skill", record=None):
        skill = self.root / name
        skill.mkdir()
        (skill / "SKILL.md").write_text("---\nname: fixture\ndescription: fixture\n---\n")
        if record is not None:
            (skill / "UPSTREAM.md").write_text(record)
        return skill

    def archive(self, sha=None, version="2.6"):
        record = "<!-- skills-check: upstream=https://example.invalid/skill.md"
        if version is not None:
            record += f" version={version}"
        if sha is not None:
            record += f" sha256={sha}"
        self.skill("doc-skill", record + " -->\n")

    def run_check(self, *args, code=0, **env):
        result = subprocess.run(["/bin/bash", str(SCRIPT), *args], env={**self.env, **env},
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout

    def test_current_git_unchanged(self):
        self.skill()
        self.assertIn("UNCHANGED", self.run_check())

    def test_git_behind(self):
        self.skill()
        self.assertIn("BEHIND", self.run_check(code=2, FAKE_BEHIND="3"))

    def test_fetch_failure_never_reports_sync(self):
        self.skill()
        out = self.run_check(code=3, FAKE_FETCH_FAIL="1")
        self.assertIn("UNKNOWN fetch失败", out)
        self.assertNotIn("UNCHANGED", out)

    def test_offline_uses_cache_not_current(self):
        self.skill()
        self.assertIn("CACHED", self.run_check("--no-fetch", code=3))
        self.assertNotIn("fetch --quiet", self.log.read_text())

    def test_offline_behind_keeps_both_flags(self):
        self.skill()
        self.assertIn("updates=1 unknown=1", self.run_check("--no-fetch", code=3, FAKE_BEHIND="2"))

    def test_local_repo_does_not_fetch(self):
        self.skill()
        self.assertIn("本地仓无上游", self.run_check(FAKE_LOCAL="1"))
        self.assertNotIn("fetch --quiet", self.log.read_text())

    def test_missing_remote_branch(self):
        self.skill()
        self.assertIn("UNKNOWN 无可用远端分支", self.run_check(code=3, FAKE_NO_BRANCH="1"))

    def test_same_version_changed_hash(self):
        self.archive("a" * 64)
        self.assertIn("CONTENT_CHANGED", self.run_check(code=2))

    def test_same_version_missing_hash_is_unknown(self):
        self.archive()
        out = self.run_check(code=3)
        self.assertIn("UNKNOWN 缺少有效 sha256", out)
        self.assertIn("updates=0 unknown=1", out)
        self.assertNotIn("CONTENT_CHANGED 上游内容已变", out)

    def test_verified_archive(self):
        self.archive(hashlib.sha256(PAYLOAD).hexdigest())
        self.assertIn("UNCHANGED", self.run_check())

    def test_version_changed_still_checks_hash(self):
        self.archive("a" * 64, version="2.5")
        out = self.run_check(code=2)
        self.assertIn("VERSION_CHANGED", out)
        self.assertIn("CONTENT_CHANGED", out)

    def test_version_change_with_missing_baseline(self):
        self.archive(version="2.5")
        self.assertIn("updates=1 unknown=1", self.run_check(code=3))

    def test_unreachable_and_empty_response_are_unknown(self):
        self.archive("a" * 64)
        for key in ["FAKE_CURL_FAIL", "FAKE_CURL_EMPTY"]:
            with self.subTest(key=key):
                self.assertIn("UNKNOWN 上游取不到", self.run_check(code=3, **{key: "1"}))

    def test_archive_offline_no_curl(self):
        self.archive("a" * 64)
        self.assertIn("UNKNOWN 离线跳过", self.run_check("--no-fetch", code=3))
        self.assertNotIn("curl ", self.log.read_text())

    def test_documented_local_source(self):
        self.skill("doc-local", "本地真源，无上游\n")
        self.assertIn("本地真源", self.run_check())

    def test_blind_source(self):
        self.skill("doc-blind")
        self.assertIn("unknown=1", self.run_check(code=3))

    def test_updates_and_network_unknown(self):
        self.skill()
        self.archive("a" * 64)
        self.assertIn("updates=1 unknown=1", self.run_check(code=3, FAKE_BEHIND="2", FAKE_CURL_FAIL="1"))

    def test_invalid_argument_is_own_error(self):
        self.run_check("--bad-flag", code=1)


if __name__ == "__main__":
    unittest.main()
