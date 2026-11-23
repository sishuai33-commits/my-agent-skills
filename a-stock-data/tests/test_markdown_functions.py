"""Offline fixtures: execute only selected function ASTs, never Markdown examples."""
import ast
from datetime import datetime, timedelta
from pathlib import Path
import re
from types import SimpleNamespace
import unittest
import urllib.request

SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
REFERENCES_DIR = SKILL_DIR / "references"
EXPECTED_REFERENCE_FILES = [
    "layer1-quote.md",
    "layer2-research.md",
    "layer3-signals.md",
    "layer4-capital-chips.md",
    "layer5-news.md",
    "layer6-fundamentals.md",
    "layer7-announcements.md",
    "workflows-and-faq.md",
]


def _markdown_sources():
    sources = [SKILL]
    if REFERENCES_DIR.is_dir():
        sources.extend(sorted(REFERENCES_DIR.glob("*.md")))
    return sources


def load_function(name, namespace):
    for md_file in _markdown_sources():
        for block in re.findall(r"```python\n(.*?)```", md_file.read_text(encoding="utf-8"), re.S):
            if f"def {name}(" not in block:
                continue
            tree = ast.parse(block)
            fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name), None)
            if fn is None:
                continue
            exec(compile(ast.Module(body=[fn], type_ignores=[]), str(md_file), "exec"), namespace)
            return namespace[name]
    raise AssertionError(name)


class QuoteTests(unittest.TestCase):
    def setUp(self):
        self.requests = []

        def urlopen(request, timeout):
            self.requests.append(request.full_url)
            rows = []
            for symbol in request.full_url.split("q=", 1)[1].split(","):
                fields = [""] * 53
                fields[1] = symbol
                fields[3] = "12.5"
                rows.append(f'v_{symbol}="' + "~".join(fields) + '";')
            return SimpleNamespace(read=lambda: "\n".join(rows).encode("gbk"))

        namespace = {"urllib": SimpleNamespace(request=SimpleNamespace(
            Request=urllib.request.Request, urlopen=urlopen))}
        self.quote = load_function("tencent_quote", namespace)

    def test_same_number_index_and_stock(self):
        result = self.quote(["000001", "sh000001", "sz000001"])
        self.assertEqual(set(result), {"000001", "sh000001", "sz000001"})
        self.assertEqual(result["000001"]["name"], "sz000001")
        self.assertEqual(result["sh000001"]["name"], "sh000001")
        self.assertEqual(self.requests[0].split("q=")[1], "sz000001,sh000001")

    def test_indices_and_etfs(self):
        symbols = ["sh000001", "sh000300", "sz399006", "sh510050", "sh510300"]
        self.assertEqual(set(self.quote(symbols)), set(symbols))
        self.assertEqual(self.requests[0].split("q=")[1], ",".join(symbols))

    def test_bare_compatibility_and_etf(self):
        result = self.quote(["688017", "300476", "002463", "510300"])
        self.assertEqual(set(result), {"688017", "300476", "002463", "510300"})
        self.assertEqual(result["510300"]["name"], "sh510300")

    def test_explicit_case_and_suffix(self):
        self.assertEqual(set(self.quote(["SH000001", "000001.SZ", "BJ832000"])),
                         {"sh000001", "sz000001", "bj832000"})

    def test_empty_and_invalid_do_not_request(self):
        self.assertEqual(self.quote([]), {})
        for code in ["", "00001", "sh000001,sz000001", "xx000001"]:
            with self.assertRaises(ValueError):
                self.quote([code])
        self.assertEqual(self.requests, [])


class DragonTests(unittest.TestCase):
    def test_empty_board(self):
        calls = []
        def empty(*args, **kwargs):
            calls.append(args)
            return []
        fn = load_function("dragon_tiger_board", {
            "datetime": datetime, "timedelta": timedelta, "eastmoney_datacenter": empty})
        result = fn("002475", "2026-11-13")
        self.assertEqual(result, {"records": [], "seats": {"buy": [], "sell": []},
                                 "institution": {"buy_amt": 0, "sell_amt": 0, "net_amt": 0}})
        self.assertEqual(len(calls), 1)


class StructureTests(unittest.TestCase):
    def test_main_skill_is_concise_and_references_exist(self):
        lines = SKILL.read_text(encoding="utf-8").splitlines()
        self.assertLess(len(lines), 200, f"SKILL.md too long: {len(lines)} lines")
        for fname in EXPECTED_REFERENCE_FILES:
            target = REFERENCES_DIR / fname
            self.assertTrue(target.is_file(), f"Missing reference file: {target}")
        referenced = set(re.findall(r"references/[A-Za-z0-9._-]+\.md", SKILL.read_text(encoding="utf-8")))
        self.assertTrue(referenced, "SKILL.md should route to references/*.md")
        for rel in referenced:
            self.assertTrue((SKILL_DIR / rel).is_file(), f"Broken reference in SKILL.md: {rel}")

    def test_upstream_manifest_exists(self):
        upstream = SKILL_DIR / "UPSTREAM.md"
        self.assertTrue(upstream.is_file(), "Missing UPSTREAM.md")
        self.assertIn("<!-- skills-check:", upstream.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
