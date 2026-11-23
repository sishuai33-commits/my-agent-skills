"""按演示顺序读取 PPTX 的页面对象，不修改文件。"""

import argparse
import posixpath
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"
LINE_PRESETS = {"line", "lineInv", "straightConnector1"} | {
    f"{kind}Connector{n}" for kind in ("bent", "curved") for n in range(2, 6)
}


def part_relationships(package, part):
    directory, filename = posixpath.split(part)
    rels_path = posixpath.join(directory, "_rels", filename + ".rels")
    root = ET.fromstring(package.read(rels_path))
    return {
        rel.attrib["Id"]: (
            rel.attrib["Type"].rsplit("/", 1)[-1],
            posixpath.normpath(posixpath.join(directory, rel.attrib["Target"])).lstrip("/"),
        )
        for rel in root
        if rel.get("TargetMode", "Internal") == "Internal"
    }


def slide_parts(package):
    office = [target for kind, target in part_relationships(package, "").values()
              if kind == "officeDocument"]
    if len(office) != 1:
        raise ValueError("未找到唯一的演示文稿主文件")
    presentation = ET.fromstring(package.read(office[0]))
    if not presentation.tag.endswith("}presentation"):
        raise ValueError("主文件不是 PowerPoint 演示文稿")
    rels = part_relationships(package, office[0])
    for slide in presentation.findall("{*}sldIdLst/{*}sldId"):
        rel_id = next((v for k, v in slide.attrib.items() if k.endswith("}id")), None)
        if rel_id not in rels or rels[rel_id][0] != "slide":
            raise ValueError("演示页引用缺失")
        yield rels[rel_id][1]


def page_objects(container, p):
    shape_tags = {p + k for k in ("sp", "pic", "cxnSp", "graphicFrame", "grpSp")}
    for shape in container:
        if shape.tag == MC + "AlternateContent":
            branch = shape.find(MC + "Fallback")
            if branch is None:
                branch = shape.find(MC + "Choice")
            if branch is not None:
                yield from page_objects(branch, p)
        elif shape.tag in shape_tags:
            yield shape
            if shape.tag == p + "grpSp":
                yield from page_objects(shape, p)


def has_text(text_body):
    return text_body is not None and any(
        node.text and node.text.strip() for node in text_body.iterfind(".//{*}t")
    )


def inspect_slide(package, part):
    slide = ET.fromstring(package.read(part))
    p = slide.tag.split("}")[0] + "}"
    tree = slide.find(f"{p}cSld/{p}spTree")
    if tree is None:
        raise ValueError(f"未找到页面对象树（{part}）")
    shapes = list(page_objects(tree, p))
    shape_ids = {el.get("id") for shape in shapes
                 for el in shape.findall(f"*/{p}cNvPr") if el.get("id")}
    text_count = pictures = lines = connectors = attached = 0
    for shape in shapes:
        if shape.tag == p + "sp":
            text_count += has_text(shape.find(p + "txBody"))
            geometry = shape.find(f"{p}spPr/{{*}}prstGeom")
            lines += geometry is not None and geometry.get("prst") in LINE_PRESETS
        elif shape.tag == p + "graphicFrame":
            table = shape.find("{*}graphic/{*}graphicData/{*}tbl")
            text_count += has_text(table)
        elif shape.tag == p + "pic":
            pictures += 1
        elif shape.tag == p + "cxnSp":
            connectors += 1
            lines += 1
            properties = shape.find(f"{p}nvCxnSpPr/{p}cNvCxnSpPr")
            if properties is not None:
                ends = [properties.find("{*}" + tag) for tag in ("stCxn", "endCxn")]
                attached += all(end is not None and end.get("id") in shape_ids for end in ends)
    return text_count, pictures, lines, connectors, attached


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path, help="待检查的 .pptx 文件")
    path = parser.parse_args().pptx
    try:
        with ZipFile(path) as package:
            rows = [inspect_slide(package, part) for part in slide_parts(package)]
    except (OSError, BadZipFile, KeyError, ET.ParseError, ValueError) as exc:
        print(f"无法读取 {path.name}（{exc}）", file=sys.stderr)
        return 1
    print(f"{path.name}（{len(rows)} 页）")
    print("| 页 | 有文字的原生对象 | 图片 | 线（含连接符） | 连接符 | 双端绑定的连接符 |")
    print("|---:|---:|---:|---:|---:|---:|")
    for index, row in enumerate(rows, 1):
        print("| " + " | ".join(map(str, (index, *row))) + " |")
    print("按文件页序（含隐藏页），组合按子对象递归。每个含文字的形状或原生表格计一个。图表、SmartArt、母版、背景与备注均不计。")
    print("兼容分支优先取回退表示。图片只计页面图片对象；文字数为零时，需查看原图和背景才能判定是否为整页图片。")
    print("线含预设线形和连接符，也含分隔线。双端绑定表示两端都引用本页对象；未绑定也可能方向正确。请在 PowerPoint 中移动模块检查随动和落点。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
