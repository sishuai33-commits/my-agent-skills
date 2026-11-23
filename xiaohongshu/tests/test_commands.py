"""Offline shell/JS assembly and contract tests for xiaohongshu (web-access CDP)."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "SKILL.md").read_text(encoding="utf-8")
INIT = next(
    b for b in re.findall(r"```bash\n(.*?)```", TEXT, re.S)
    if b.startswith("XHS_SKILL_ROOT=")
)

FAKE_CURL_SCRIPT = """#!{python}
import json
import os
import sys

log_path = os.environ.get("FAKE_CURL_LOG")
stdin_data = sys.stdin.read() if not sys.stdin.isatty() else ""
record = {{"argv": sys.argv[1:], "stdin": stdin_data}}
if log_path:
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\\n")

mode = os.environ.get("FAKE_CURL_MODE", "eval_ok")
proxy = os.environ.get("XHS_CDP_PROXY", "http://localhost:3456")
url = next((a for a in sys.argv[1:] if a.startswith(proxy)), "")
if "/new" in url:
    if mode == "new_error":
        print(json.dumps({{"error": "cannot create tab"}}))
    else:
        print(json.dumps({{"targetId": os.environ.get("FAKE_TARGET_ID", "TAB_OWNED_01")}}))
elif "/eval" in url:
    if mode == "eval_error":
        print(json.dumps({{"error": "Runtime.evaluate failed"}}))
    else:
        print(json.dumps({{"value": json.dumps({{"ok": True, "bytes": len(stdin_data)}})}}))
elif "/navigate" in url:
    print(json.dumps({{"navigated": True}}))
elif "/scroll" in url:
    print(json.dumps({{"scrolled": True}}))
elif "/close" in url:
    print(json.dumps({{"success": True}}))
else:
    print(json.dumps({{"status": "ok", "connected": True}}))
"""


class CommandsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="xhs-offline-")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.log_path = self.home / "curl.jsonl"
        bin_dir = self.home / "bin"
        bin_dir.mkdir()
        fake_curl = bin_dir / "curl"
        fake_curl.write_text(FAKE_CURL_SCRIPT.format(python=sys.executable), encoding="utf-8")
        fake_curl.chmod(0o700)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "FAKE_CURL_LOG": str(self.log_path),
            "XHS_CDP_PROXY": "http://localhost:3456",
        }
        for key in ("XHS_SKILL_ROOT", "XHS_SKILL_MD", "XHS_TARGET_ID", "XHS_TARGET_OWNED"):
            self.env.pop(key, None)

    def read_curl_calls(self):
        if not self.log_path.exists():
            return []
        lines = [line for line in self.log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return [json.loads(line) for line in lines]

    def clear_curl_calls(self):
        if self.log_path.exists():
            self.log_path.unlink()

    def run_shell(self, command, extra_env=None):
        env = {**self.env, **(extra_env or {})}
        return subprocess.run(
            ["/bin/bash", "-c", INIT + "\n" + command],
            cwd="/",
            env=env,
            capture_output=True,
            text=True,
        )

    def run_node_extract(self, script_name, script_args, window_state):
        js = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script_name), *script_args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        code = (
            "global.window = JSON.parse(process.argv[1]);"
            "console.log(eval(process.argv[2]));"
        )
        res = subprocess.run(
            ["node", "-e", code, json.dumps(window_state), js],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(res.stdout), js

    def test_skill_md_frontmatter_and_cdp_contract(self):
        match = re.match(r"^---\n(.*?)\n---", TEXT, re.S)
        self.assertIsNotNone(match)
        fm = yaml.safe_load(match.group(1))
        self.assertEqual(fm["name"], "xiaohongshu")
        self.assertIn("web-access", fm["description"])
        self.assertNotIn("browser-act", fm["description"])
        self.assertNotIn("category", fm)
        self.assertNotIn("source", fm)
        meta = fm["metadata"]
        self.assertEqual(str(meta["version"]), "2.0.0")
        self.assertEqual(meta["requires"], "web-access")
        self.assertEqual(meta["category"], "infra")
        self.assertEqual(meta["source"], "self-built")
        self.assertEqual(meta["last_modified"], "2026-11-23")

        # No deprecated browser-act or hardcoded host skill directory
        self.assertNotIn("browser-act", TEXT)
        self.assertNotIn("$HOME/.claude/skills", TEXT)
        self.assertNotIn("~/.claude/skills", TEXT)
        self.assertNotIn('eval "$(python', TEXT)

        # Core web-access CDP contract & safety rules
        for token in (
            "check-deps.mjs",
            "/new",
            "/navigate?target=",
            "/eval?target=",
            "/scroll?target=",
            "/close?target=",
            "--data-binary @-",
            "--data-raw",
            "XHS_TARGET_OWNED",
            "严禁把 JS 交给 shell 的 `eval`",
            "不无限滚动",
            "按 id 去重",
            "反爬",
        ):
            self.assertIn(token, TEXT)

    def test_path_resolution_supports_loaded_skill_md_and_canonical_fallback(self):
        # 1) Loaded SKILL.md symlink under non-.claude host dir resolves to canonical ROOT
        dsh_link = self.home / ".dsh/skills/xiaohongshu"
        dsh_link.parent.mkdir(parents=True)
        dsh_link.symlink_to(ROOT, target_is_directory=True)
        res1 = self.run_shell(
            'printf "%s" "$XHS_SKILL_ROOT"',
            extra_env={"XHS_SKILL_MD": str(dsh_link / "SKILL.md")},
        )
        self.assertEqual(res1.returncode, 0, res1.stderr)
        self.assertEqual(Path(res1.stdout), ROOT.resolve())

        # 2) Isolated HOME with no XHS_SKILL_MD falls back to canonical ROOT
        res2 = self.run_shell('printf "%s" "$XHS_SKILL_ROOT"')
        self.assertEqual(res2.returncode, 0, res2.stderr)
        self.assertEqual(Path(res2.stdout), ROOT.resolve())

    def test_all_documented_extractions_use_web_access_eval_via_stdin(self):
        commands = re.findall(r"^xhs_extract .*", TEXT, re.M)
        self.assertEqual(len(commands), 6)
        for command in commands:
            with self.subTest(command=command):
                self.clear_curl_calls()
                result = self.run_shell(command, extra_env={"XHS_TARGET_ID": "TAB_42"})
                self.assertEqual(result.returncode, 0, result.stderr)
                parsed_out = json.loads(result.stdout)
                self.assertTrue(parsed_out["ok"])

                calls = self.read_curl_calls()
                self.assertEqual(len(calls), 1)
                argv = calls[0]["argv"]
                stdin_js = calls[0]["stdin"]
                self.assertIn("POST", argv)
                self.assertIn("http://localhost:3456/eval?target=TAB_42", argv)
                self.assertIn("--data-binary", argv)
                self.assertIn("@-", argv)
                self.assertIn("(function()", stdin_js)
                self.assertIn("\n", stdin_js)

                # Verify exact stdin JS parses cleanly in Node (newlines preserved for // comments)
                syntax_check = subprocess.run(
                    ["node", "-e", "new Function(process.argv[1]);", stdin_js],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(syntax_check.returncode, 0, syntax_check.stderr)

    def test_empty_js_does_not_invoke_browser(self):
        root = self.home / "root with spaces"
        (root / "scripts").mkdir(parents=True)
        (root / "scripts/empty.py").write_text("print('   ')\n", encoding="utf-8")
        result = self.run_shell(
            f'XHS_SKILL_ROOT="{root}"\nXHS_TARGET_ID="TAB_1"\nxhs_extract empty.py'
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("未生成 JavaScript", result.stderr)
        self.assertEqual(self.read_curl_calls(), [])

    def test_missing_script_and_missing_target_do_not_invoke_browser(self):
        res_missing = self.run_shell("xhs_extract absent.py", extra_env={"XHS_TARGET_ID": "TAB_1"})
        self.assertNotEqual(res_missing.returncode, 0)
        self.assertEqual(res_missing.stdout, "")
        self.assertEqual(self.read_curl_calls(), [])

        res_no_tab = self.run_shell("xhs_extract extract-search.py")
        self.assertNotEqual(res_no_tab.returncode, 0)
        self.assertIn("XHS_TARGET_ID", res_no_tab.stderr)
        self.assertEqual(self.read_curl_calls(), [])

    def test_cdp_proxy_error_response_fails_nonzero(self):
        res = self.run_shell(
            "xhs_extract extract-search.py",
            extra_env={"XHS_TARGET_ID": "TAB_1", "FAKE_CURL_MODE": "eval_error"},
        )
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Runtime.evaluate failed", res.stderr)

    def test_tab_lifecycle_and_owned_cleanup_boundary(self):
        # 1) Full owned tab lifecycle: open -> navigate (with & in query) -> scroll -> close
        note_url = "https://www.xiaohongshu.com/explore/abc123?xsec_token=TOK_1&xsec_source=pc_search"
        res = self.run_shell(
            f'xhs_open_tab "https://www.xiaohongshu.com" >/dev/null\n'
            f'xhs_navigate "{note_url}" >/dev/null\n'
            f'xhs_scroll 3000 down >/dev/null\n'
            f'xhs_close_tab\n'
            f'printf "%s|%s" "$XHS_TARGET_ID" "$XHS_TARGET_OWNED"',
            extra_env={"FAKE_TARGET_ID": "TAB_MINE_99"},
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(res.stdout, "|0")
        calls = self.read_curl_calls()
        self.assertEqual(len(calls), 4)
        self.assertIn("http://localhost:3456/new", calls[0]["argv"])
        self.assertIn("--data-raw", calls[0]["argv"])
        self.assertIn("http://localhost:3456/navigate?target=TAB_MINE_99", calls[1]["argv"])
        self.assertIn(note_url, calls[1]["argv"])
        self.assertIn("http://localhost:3456/scroll?target=TAB_MINE_99&y=3000&direction=down", calls[2]["argv"])
        self.assertIn("http://localhost:3456/close?target=TAB_MINE_99", calls[3]["argv"])

        # 2) Unowned user tab MUST NOT be closed
        self.clear_curl_calls()
        res_unowned = self.run_shell(
            'XHS_TARGET_ID="USER_EXISTING_TAB"\nXHS_TARGET_OWNED=0\nxhs_close_tab'
        )
        self.assertEqual(res_unowned.returncode, 0, res_unowned.stderr)
        self.assertEqual(self.read_curl_calls(), [])

        # 3) Failed /new must not mark ownership
        self.clear_curl_calls()
        res_fail = self.run_shell(
            'xhs_open_tab "https://www.xiaohongshu.com" || true\nprintf "%s|%s" "$XHS_TARGET_ID" "$XHS_TARGET_OWNED"',
            extra_env={"FAKE_CURL_MODE": "new_error"},
        )
        self.assertEqual(res_fail.stdout, "|0")

    def test_extract_search_slice_and_empty_and_invalid_args(self):
        feeds = [
            {
                "id": str(i),
                "xsecToken": f"tok-{i}",
                "noteCard": {
                    "type": "normal",
                    "displayTitle": f"title-{i}",
                    "user": {"userId": f"u-{i}", "nickname": f"nick-{i}"},
                    "interactInfo": {"likedCount": "10", "collectedCount": "5", "commentCount": "2"},
                    "cover": {"url_default": f"https://img/{i}.jpg"},
                },
            }
            for i in range(45)
        ]
        obj, _ = self.run_node_extract(
            "extract-search.py",
            ["--offset", "20", "--limit", "20"],
            {"__INITIAL_STATE__": {"search": {"feeds": feeds, "hasMore": False, "searchContext": {"page": 2}}}},
        )
        self.assertEqual([x["id"] for x in obj["items"]], list(map(str, range(20, 40))))
        self.assertEqual((obj["total"], obj["offset"], obj["returned"], obj["nextOffset"]), (45, 20, 20, 40))
        self.assertFalse(obj["hasMore"])
        self.assertEqual(obj["page"], 2)
        self.assertEqual(obj["items"][0]["xsecToken"], "tok-20")
        self.assertEqual(obj["items"][0]["title"], "title-20")
        self.assertEqual(obj["items"][0]["coverUrl"], "https://img/20.jpg")

        for args in [("--offset", "-1"), ("--limit", "0")]:
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/extract-search.py"), *args],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")

        empty_obj, _ = self.run_node_extract("extract-search.py", [], {})
        self.assertIs(empty_obj["error"], True)

    def test_extract_note_detail_contract(self):
        fixture = {
            "__INITIAL_STATE__": {
                "note": {
                    "noteDetailMap": {
                        "note-1": {
                            "note": {
                                "noteId": "note-1",
                                "title": {"value": "测试标题"},
                                "desc": {"_value": "正文内容"},
                                "type": "normal",
                                "time": 1748390400000,
                                "ipLocation": "上海",
                                "user": {"userId": "u1", "nickname": "作者A", "avatar": "https://img/a.jpg"},
                                "interactInfo": {
                                    "likedCount": "100",
                                    "collectedCount": "50",
                                    "commentCount": "12",
                                    "shareCount": "3",
                                },
                                "tagList": [{"name": "旅行", "type": "topic"}],
                                "imageList": [{}, {}, {}],
                            }
                        }
                    }
                }
            }
        }
        obj, _ = self.run_node_extract("extract-note-detail.py", ["note-1"], fixture)
        self.assertEqual(obj["noteId"], "note-1")
        self.assertEqual(obj["title"], "测试标题")
        self.assertEqual(obj["desc"], "正文内容")
        self.assertEqual(obj["nickname"], "作者A")
        self.assertEqual(obj["likedCount"], "100")
        self.assertEqual(obj["tagList"], [{"name": "旅行", "type": "topic"}])
        self.assertEqual(obj["imageCount"], 3)

        err_obj, _ = self.run_node_extract("extract-note-detail.py", ["missing"], fixture)
        self.assertIs(err_obj["error"], True)

    def test_extract_note_comments_contract(self):
        fixture = {
            "__INITIAL_STATE__": {
                "note": {
                    "noteDetailMap": {
                        "note-1": {
                            "comments": {
                                "cursor": "cur-1",
                                "hasMore": True,
                                "list": [
                                    {
                                        "id": "c-1",
                                        "content": "很实用",
                                        "likeCount": "23",
                                        "createTime": 1748390500000,
                                        "ipLocation": "广东",
                                        "userInfo": {
                                            "userId": "u2",
                                            "nickname": "评论者B",
                                            "image": "https://img/b.jpg",
                                        },
                                    }
                                ],
                            }
                        }
                    }
                }
            }
        }
        obj, _ = self.run_node_extract("extract-note-comments.py", ["note-1"], fixture)
        self.assertEqual(obj["count"], 1)
        self.assertEqual(obj["cursor"], "cur-1")
        self.assertTrue(obj["hasMore"])
        self.assertEqual(obj["comments"][0]["id"], "c-1")
        self.assertEqual(obj["comments"][0]["nickname"], "评论者B")
        self.assertEqual(obj["comments"][0]["avatar"], "https://img/b.jpg")

        err_obj, _ = self.run_node_extract("extract-note-comments.py", ["note-1"], {})
        self.assertIs(err_obj["error"], True)

    def test_extract_user_profile_contract(self):
        fixture = {
            "__INITIAL_STATE__": {
                "user": {
                    "userPageData": {
                        "basicInfo": {
                            "nickname": "博主C",
                            "desc": "简介",
                            "gender": 1,
                            "ipLocation": "北京",
                            "imageb": "https://img/c.jpg",
                        },
                        "interactions": [
                            {"type": "follows", "count": "10"},
                            {"type": "fans", "count": "200"},
                            {"type": "interaction", "count": "3000"},
                        ],
                        "tags": [{"name": "科技"}, {"name": "效率"}],
                    }
                }
            }
        }
        obj, _ = self.run_node_extract("extract-user-profile.py", ["user-9"], fixture)
        self.assertEqual(obj["userId"], "user-9")
        self.assertEqual(obj["nickname"], "博主C")
        self.assertEqual(obj["follows"], "10")
        self.assertEqual(obj["fans"], "200")
        self.assertEqual(obj["interaction"], "3000")
        self.assertEqual(obj["tags"], ["科技", "效率"])

        err_obj, _ = self.run_node_extract("extract-user-profile.py", ["user-9"], {})
        self.assertIs(err_obj["error"], True)

    def test_extract_user_notes_contract(self):
        fixture = {
            "__INITIAL_STATE__": {
                "user": {
                    "hasMore": False,
                    "notes": [
                        {
                            "0": {
                                "noteCard": {
                                    "type": "normal",
                                    "displayTitle": "笔记1",
                                    "interactInfo": {"likedCount": "1", "collectedCount": "2", "commentCount": "3"},
                                    "cover": {"url": "https://img/n1.jpg"},
                                }
                            },
                            "1": {
                                "noteCard": {
                                    "type": "video",
                                    "displayTitle": "笔记2",
                                    "interactInfo": {"likedCount": "4", "collectedCount": "5", "commentCount": "6"},
                                    "cover": {"url_default": "https://img/n2.jpg"},
                                }
                            },
                            "2": {
                                "noteCard": {
                                    "type": "normal",
                                    "displayTitle": "笔记3",
                                    "interactInfo": {"likedCount": "7", "collectedCount": "8", "commentCount": "9"},
                                    "cover": {"url": "https://img/n3.jpg"},
                                }
                            },
                        }
                    ],
                }
            }
        }
        obj, _ = self.run_node_extract("extract-user-notes.py", ["--limit", "2"], fixture)
        self.assertEqual(obj["total"], 2)
        self.assertFalse(obj["hasMore"])
        self.assertIsNone(obj["notes"][0]["id"])
        self.assertEqual([n["title"] for n in obj["notes"]], ["笔记1", "笔记2"])
        self.assertEqual(obj["notes"][1]["coverUrl"], "https://img/n2.jpg")

        err_obj, _ = self.run_node_extract("extract-user-notes.py", [], {})
        self.assertIs(err_obj["error"], True)


if __name__ == "__main__":
    unittest.main()
