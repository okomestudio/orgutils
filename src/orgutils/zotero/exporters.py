"""Zotero exporters."""
import subprocess
from collections import namedtuple
from typing import List
from xml.etree import ElementTree as ET

from ..org import structs
from . import db
from ..utils import remove_extra_whitespaces


def list_items():  # noqa
    rows = db.get_item_list()
    print("\t".join(["ID", "Annotation Count", "File"]))
    for row in rows:
        print(f"{ row['id'] }\t{ row['annotationCount'] }\t\"{ row['filename'] }\"")


Item = namedtuple("Item", ("loc", "object"))


def _get_outline(filename: str) -> List[Item] | None:
    """Get document outline (table of contents)."""
    outline_xml = subprocess.check_output(["dumppdf.py", "-T", filename])

    try:
        root = ET.fromstring(outline_xml)
    except ET.ParseError:
        return

    if not root:
        return

    items = []
    for elmt in root.findall(".//outline[@title]"):
        page = int(elmt.find("pageno").text)
        numbers = elmt.findall(".//number")
        x = float(numbers[0].text)
        y = float(numbers[1].text)
        title = elmt.get("title")
        level = int(elmt.get("level"))

        obj = structs.Heading(
            title,
            level + 1,
            {"page": page, "pos_x": x, "pos_y": y},
        )
        items.append(Item((page, -y, x), obj))

    return items


def export_to_org(id):  # noqa
    filename = db.get_filename_for_id(id)

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
            x, y = None, None
        text = row["text"]
        comment = row["comment"]

        objs = []
        if text:
            objs.append(
                structs.QuoteBlock(remove_extra_whitespaces(text) + f" (p. { page })")
            )
        if comment:
            objs.append(structs.Paragraph(comment + f" (p. { page })"))
        if objs:
            items.append(Item((page, -y, x), structs.Group(objs)))

    items = [Item((-1, 0, 0), structs.Heading("Highlights & notes", 1, {}))] + sorted(
        items, key=lambda item: item.loc
    )

    print(structs.dumps((item.object for item in items)))
