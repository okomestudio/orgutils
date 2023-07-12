"""Zotero exporters."""
import subprocess
import xml.dom.minidom
from collections import namedtuple
from xml.etree import ElementTree as ET

from ..org import structs
from . import db


def list_items():  # noqa
    conn = db.connect()
    cur = conn.cursor()
    cur.execute(db.SQL_LIST_ITEMS)
    rows = cur.fetchall()
    print(("ID", "Annotation Count", "File"))
    print(rows)


def _pretty_xml(tree):
    dom = xml.dom.minidom.parseString(ET.tostring(tree))
    return dom.toprettyxml(indent=" " * 2)


def export_to_org(id):  # noqa
    filename = db.get_filename_for_id(id)

    outline_xml = subprocess.check_output(["dumppdf.py", "-T", filename])
    elmt = ET.fromstring(outline_xml)

    Item = namedtuple("Item", ("page", "object"))

    items = []
    for elmt in elmt.findall(".//outline[@title]"):
        page = int(elmt.find("pageno").text)
        obj = structs.Heading(elmt.get("title"), int(elmt.get("level")), {"page": page})
        items.append(Item(page, obj))

    for row in db.get_annotations_for_id(id):
        page = int(row[0])
        text = row[1]
        comment = row[2]

        objs = []
        if text:
            objs.append(structs.QuoteBlock(text + f" (p. { page })"))
        if comment:
            objs.append(structs.Paragraph(comment + f" (p. { page })"))
        if objs:
            if len(objs) > 1:
                items.append((page, structs.Group(objs)))
            else:
                items.append((page, objs[0]))

    items = sorted(items, key=lambda o: o[0])

    for page, item in items:
        print("\n".join(item.render()))
        print()
