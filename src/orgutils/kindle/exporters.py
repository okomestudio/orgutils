"""Kindle highlights to Org converter.

Use Bookcision to JSON export Kindle highlights and notes in Amazon Cloud Reader. Then
feed that file to this script to import as Org file.

TODO: Rewrite in Emacs Lisp.
"""
import json
import re

from ..org import structs
from .. import utils


def _inspect_target_file(target_file):
    raise NotImplementedError
    if target_file:
        with open(target_file):
            root = orgparse.load(f)

        def find_target(node, target_heading, depth):
            if node.heading == target_heading:
                return node, depth
            for child_node in node.children:
                result = find_target(child_node, target_heading, depth + 1)
                if result:
                    return result

        def push_headers_to(items, node, heading_depth=1):
            for child in node.children:
                loc = child.get_property("KINDLE_LOC")
                if loc:
                    loc = int(loc)
                    items.append(
                        (
                            loc,
                            {
                                "text": child.heading,
                                "location": {"value": loc},
                                "note": f"H{ heading_depth + 1}",
                            },
                        )
                    )
                    push_headers_to(items, child, heading_depth + 1)

        target, base_heading_depth = find_target(root, "That", 0)
        if target:
            push_headers_to(sorted_items, target)


def export_to_org(dump, lang):  # noqa
    with open(dump) as f:
        jd = json.load(f)

    preprocess = (
        utils.remove_whitespaces_between_zenkaku if lang == "ja" else lambda s: s
    )

    title = preprocess(jd["title"])
    authors = jd["authors"]
    asin = jd["asin"]
    highlights = jd["highlights"]

    sorted_items = [(x["location"]["value"], x) for x in highlights]

    base_heading_depth = 1
    sorted_items = sorted(
        sorted_items,
        key=lambda tpl: (
            tpl[0],
            (
                -1
                if (tpl[1].get("note") or "").startswith("h")
                or (tpl[1].get("note") or "").startswith("H")
                else 0
            ),
        ),
    )

    # build org tree
    org = []
    org.append(
        structs.Heading(
            title,
            1,
            {
                "author": authors,
                "asin": asin,
            },
        )
    )

    for loc, item in sorted_items:
        m = re.match(r"^[hH](\d+)(|\s+(.*))$", item.get("note") or "")
        if m:
            heading_depth = int(m.group(1))
            org.append(
                structs.Heading(
                    preprocess(item["text"] or m.group(3) or "--MISSING--"),
                    heading_depth + base_heading_depth,
                    {"kindle_loc": item["location"]["value"]},
                )
            )
            continue

        org.append(
            structs.QuoteBlock(
                f"{ preprocess(item['text']) } (loc. { item['location']['value'] })"
            )
        )
        if item.get("note"):
            org.append(structs.Paragraph(item["note"]))

    # render org doc
    print(structs.dumps(org))
