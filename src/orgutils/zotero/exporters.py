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


def export_to_org(id):  # noqa
    filename = db.get_filename_for_id(id)

    Item = namedtuple("Item", ("loc", "object"))
    items: List[Item] = []

    # Get document outline (table of contents).
    outline_xml = subprocess.check_output(["dumppdf.py", "-T", filename])
    for elmt in ET.fromstring(outline_xml).findall(".//outline[@title]"):
        page = int(elmt.find("pageno").text)
        numbers = elmt.findall(".//number")
        x = float(numbers[0].text)
        y = float(numbers[1].text)
        title = elmt.get("title")
        level = int(elmt.get("level"))

        obj = structs.Heading(
            title,
            level,
            {"page": page, "pos_x": x, "pos_y": y},
        )
        items.append(Item((page, -y, x), obj))

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

    print(
        structs.dumps(
            (item.object for item in sorted(items, key=lambda item: item.loc))
        )
    )
