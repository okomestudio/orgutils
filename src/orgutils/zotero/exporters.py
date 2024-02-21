"""Zotero exporters."""
import subprocess
from collections import namedtuple
from pathlib import Path
from typing import List
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from ..org import structs
from ..utils import remove_whitespaces_between_zenkaku
from . import db


def list_items() -> None:
    rows = db.get_item_list()
    print("\t".join(["ID", "Annotation Count", "File"]))
    for row in rows:
        print(f"{ row['id'] }\t{ row['annotationCount'] }\t\"{ row['filename'] }\"")


Item = namedtuple("Item", ("loc", "object"))


def _element_find(elmt: Element, path: str) -> Element:
    e = elmt.find(path)
    if not e:
        raise RuntimeError(f"Element not found at {path}")
    return e


def _element_findall(elmt: Element, path: str) -> List[Element]:
    e = elmt.findall(path)
    if not e:
        raise RuntimeError(f"Element items not found at {path}")
    return e


def _element_text(elmt: Element) -> str:
    if elmt.text is None:
        raise RuntimeError("Element.text attribute returns None")
    return elmt.text


def _get_outline(filename: str | Path) -> List[Item] | None:
    """Get document outline (table of contents)."""
    outline_xml = subprocess.check_output(["dumppdf.py", "-T", filename])

    try:
        root = ET.fromstring(outline_xml)
    except ET.ParseError:
        return None

    if not root:
        return None

    items = []
    for elmt in root.findall(".//outline[@title]"):
        page = int(_element_text(_element_find(elmt, "pageno")))
        numbers = _element_findall(elmt, ".//number")
        x = float(_element_text(numbers[0]))
        y = float(_element_text(numbers[1]))
        title = elmt.get("title")
        level = int(elmt.get("level", -1))
        if title is None:
            raise RuntimeError("'title' not found")
        if level < 0:
            raise RuntimeError("'level' not found")

        obj = structs.Heading(
            title,
            level + 1,
            {"page": page, "pos_x": x, "pos_y": y},
        )
        items.append(Item((page, -y, x), obj))

    return items


def export_to_org(id: str, lang: str) -> None:
    filename = db.get_filename_for_id(id)
    # preprocess = preprocess_ja if lang == "ja" else lambda s: s

    items: List[Item] = []

    outline_items = _get_outline(filename)
    if outline_items:
        items.extend(outline_items)

    # Get annotations.
    for row in db.get_annotations_for_id(id):
        page = row["page"]
        rects = row["position"].get("rects")
        if rects:
            first = rects[0]
            x, y = float(first[0]), float(first[-1])
        else:
            raise RuntimeError('"rects" not found')
        text = row["text"]
        comment = row["comment"]

        objs: List[structs.OrgObject] = []
        if text:
            objs.append(
                structs.QuoteBlock(
                    remove_whitespaces_between_zenkaku(text) + f" (p. { page })"
                )
            )
        if comment:
            objs.append(structs.Paragraph(comment + f" (p. { page })"))
        if objs:
            items.append(Item((page, -y, x), structs.Group(objs)))

    items = [Item((-1, 0, 0), structs.Heading("Highlights & notes", 1, {}))] + sorted(
        items, key=lambda item: item.loc
    )

    print(structs.dumps((item.object for item in items)))
