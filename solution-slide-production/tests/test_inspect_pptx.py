"""Minimal CLI tests for scripts/inspect_pptx.py using in-memory/temp PPTX zips."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inspect_pptx.py"

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    Target="ppt/presentation.xml"/>
</Relationships>
"""

PRESENTATION_XML = """<?xml version="1.0" encoding="UTF-8"?>
<p:presentation
  xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:sldIdLst>
    <p:sldId id="256" r:id="rId1"/>
  </p:sldIdLst>
</p:presentation>
"""

PRESENTATION_RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
    Target="slides/slide1.xml"/>
</Relationships>
"""

SLIDE1_XML = """<?xml version="1.0" encoding="UTF-8"?>
<p:sld
  xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="Box A"/></p:nvSpPr>
        <p:txBody><a:p><a:r><a:t>模块A</a:t></a:r></a:p></p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="3" name="Box B"/></p:nvSpPr>
        <p:txBody><a:p><a:r><a:t>模块B</a:t></a:r></a:p></p:txBody>
      </p:sp>
      <p:pic>
        <p:nvPicPr><p:cNvPr id="4" name="Image 1"/></p:nvPicPr>
      </p:pic>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="5" name="Divider Line"/></p:nvSpPr>
        <p:spPr><a:prstGeom prst="line"/></p:spPr>
      </p:sp>
      <p:cxnSp>
        <p:nvCxnSpPr>
          <p:cNvPr id="6" name="Attached Connector"/>
          <p:cNvCxnSpPr>
            <a:stCxn id="2" idx="0"/>
            <a:endCxn id="3" idx="0"/>
          </p:cNvCxnSpPr>
        </p:nvCxnSpPr>
      </p:cxnSp>
      <p:cxnSp>
        <p:nvCxnSpPr>
          <p:cNvPr id="7" name="Loose Connector"/>
          <p:cNvCxnSpPr/>
        </p:nvCxnSpPr>
      </p:cxnSp>
    </p:spTree>
  </p:cSld>
</p:sld>
"""


def write_minimal_pptx(dest: Path) -> None:
    with ZipFile(dest, "w") as zf:
        zf.writestr("_rels/.rels", ROOT_RELS)
        zf.writestr("ppt/presentation.xml", PRESENTATION_XML)
        zf.writestr("ppt/_rels/presentation.xml.rels", PRESENTATION_RELS)
        zf.writestr("ppt/slides/slide1.xml", SLIDE1_XML)


class InspectPptxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="inspect-pptx-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def run_cli(self, target: Path):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(target)],
            cwd=str(self.root),
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_valid_minimal_pptx_counts(self):
        pptx = self.root / "sample.pptx"
        write_minimal_pptx(pptx)
        res = self.run_cli(pptx)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("sample.pptx（1 页）", res.stdout)
        # 2 text shapes, 1 picture, 3 lines (1 line shape + 2 connectors), 2 connectors, 1 double-attached
        self.assertIn("| 1 | 2 | 1 | 3 | 2 | 1 |", res.stdout)

    def test_invalid_non_zip_file(self):
        bad = self.root / "broken.pptx"
        bad.write_text("not a zip archive", encoding="utf-8")
        res = self.run_cli(bad)
        self.assertEqual(res.returncode, 1)
        self.assertIn("无法读取 broken.pptx", res.stderr)

    def test_zip_missing_rels(self):
        bad_zip = self.root / "empty.pptx"
        with ZipFile(bad_zip, "w") as zf:
            zf.writestr("dummy.txt", "hello")
        res = self.run_cli(bad_zip)
        self.assertEqual(res.returncode, 1)
        self.assertIn("无法读取 empty.pptx", res.stderr)

    def test_missing_file(self):
        missing = self.root / "does-not-exist.pptx"
        res = self.run_cli(missing)
        self.assertEqual(res.returncode, 1)
        self.assertIn("无法读取 does-not-exist.pptx", res.stderr)


if __name__ == "__main__":
    unittest.main()
