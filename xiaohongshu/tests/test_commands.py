"""Offline shell/JS assembly tests. browser-act is always a local fake."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "SKILL.md").read_text()
INIT = next(b for b in re.findall(r"```bash\n(.*?)```", TEXT, re.S)
            if b.startswith("XHS_SKILL_ROOT="))


class CommandsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="xhs-offline-")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        link = self.home / ".claude/skills/xiaohongshu"
        link.parent.mkdir(parents=True)
        link.symlink_to(ROOT, target_is_directory=True)
        bin_dir = self.home / "bin"
        bin_dir.mkdir()
        fake = bin_dir / "browser-act"
        fake.write_text(f"#!{sys.executable}\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n")
        fake.chmod(0o700)
        self.env = {**os.environ, "HOME": str(self.home),
                    "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]}

    def run_shell(self, command):
        return subprocess.run(["/bin/bash", "-c", INIT + "\n" + command],
                              cwd="/", env=self.env, capture_output=True, text=True)

    def test_all_documented_extractions_use_browser_eval(self):
        commands = re.findall(r"^xhs_extract .*", TEXT, re.M)
        self.assertEqual(len(commands), 6)
        for command in commands:
            with self.subTest(command=command):
                result = self.run_shell(command)
                self.assertEqual(result.returncode, 0, result.stderr)
                args = json.loads(result.stdout)
                self.assertEqual(args[0], "--session")
                self.assertRegex(args[1], r'^xhs-[0-9a-f]{12}$')
                self.assertEqual(args[2], "eval")
                self.assertEqual(len(args), 4)
                self.assertIn("(function()", args[3])
        self.assertNotIn('eval "$(python ', TEXT)

    def test_empty_js_does_not_invoke_browser(self):
        root = self.home / "root with spaces"
        (root / "scripts").mkdir(parents=True)
        (root / "scripts/empty.py").write_text("print('   ')\n")
        result = self.run_shell(f'XHS_SKILL_ROOT="{root}"\nxhs_extract empty.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("未生成 JavaScript", result.stderr)

    def test_missing_script_does_not_invoke_browser(self):
        result = self.run_shell("xhs_extract absent.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_unique_session_per_task_and_owned_cleanup(self):
        a = json.loads(self.run_shell('xhs_extract extract-search.py').stdout)[1]
        b = json.loads(self.run_shell('xhs_extract extract-search.py').stdout)[1]
        self.assertNotEqual(a, b)
        self.assertNotIn('browser-act session close xhs`', TEXT)
        self.assertIn('"$XHS_SESSION_OWNED" = 1', TEXT)

    def test_search_second_slice_consumes_loaded_items_even_without_more_pages(self):
        js = subprocess.run([sys.executable, str(ROOT / 'scripts/extract-search.py'),
                             '--offset', '20', '--limit', '20'], check=True,
                            capture_output=True, text=True).stdout
        fixture = {'search': {'feeds': [{'id': str(i), 'noteCard': {}} for i in range(45)], 'hasMore': False}}
        code = 'global.window={__INITIAL_STATE__:JSON.parse(process.argv[1])}; console.log(eval(process.argv[2]));'
        result = subprocess.run(['node', '-e', code, json.dumps(fixture), js], check=True,
                                capture_output=True, text=True)
        obj = json.loads(result.stdout)
        self.assertEqual([x['id'] for x in obj['items']], list(map(str, range(20, 40))))
        self.assertEqual((obj['total'], obj['returned'], obj['nextOffset']), (45, 20, 40))
        self.assertFalse(obj['hasMore'])
        self.assertLess(obj['nextOffset'], obj['total'])

    def test_search_invalid_slice_fails_before_browser(self):
        for args in [('--offset', '-1'), ('--limit', '0')]:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/extract-search.py'), *args],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')

    def test_empty_page_is_explicit_error(self):
        js = subprocess.run([sys.executable, str(ROOT / "scripts/extract-search.py")],
                            check=True, capture_output=True, text=True).stdout
        result = subprocess.run(["node", "-e", "global.window={}; console.log(eval(process.argv[1]));", js],
                                check=True, capture_output=True, text=True)
        self.assertIs(json.loads(result.stdout)["error"], True)


if __name__ == "__main__":
    unittest.main()
