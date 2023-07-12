"""Kindle highlights to Org converter.

Use Bookcision to JSON export Kindle highlights and notes in Amazon Cloud Reader. Then
feed that file to this script to import as Org file.

TODO: Rewrite in Emacs Lisp.
"""
import json
import re

import orgparse


def preprocess_ja(text):
    """Preprocess Japanese text."""
    if text is None:
        return None
    text = re.sub(r"　", "  ", text)
    text = re.sub(r"(?<=\S)\s(?=\S)", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def render_header(org, item, depth):
    org.append("*" * depth + " " + item["text"])
    org.append(":PROPERTIES:")
    org.append(f":KINDLE_LOC: { item['location']['value'] }")
    org.append(":END:")
    org.append("")


def render_note(org, item):
    org.append("#+BEGIN_QUOTE")
    org.append(f"{ item['text'] } (loc. { item['location']['value'] })")
    org.append("#+END_QUOTE")
    org.append("")

    note = item.get("note")
    if note:
        org.append(note)
        org.append("")


def export_to_org(highlights, lang, target_file, target_heading):
    with open(highlights) as f:
        jd = json.load(f)

    if lang == "ja":
        preprocess = preprocess_ja
    else:
        preprocess = lambda s: s

    title = preprocess(jd["title"])
    authors = jd["authors"]
    asin = jd["asin"]
    highlights = jd["highlights"]
    for item in highlights:
        item["text"] = preprocess(item["text"])
        item["note"] = preprocess(item["note"])

    sorted_items = [(x["location"]["value"], x) for x in highlights]

    base_heading_depth = 1
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

    sorted_items = sorted(sorted_items, key=lambda tpl: (tpl[0], tpl[1]["text"]))

    # start rendering
    org = []
    org.append(f"* { title }")
    org.append(":PROPERTIES:")
    org.append(f":AUTHOR: { authors }")
    org.append(f":ASIN: { asin }")
    org.append(f":END:")
    org.append("")

    for loc, item in sorted_items:
        m = re.match(r"^[hH](\d+)$", item.get("note") or "")
        if m:
            heading_depth = int(m.group(1))
            render_header(org, item, heading_depth + base_heading_depth)
            continue

        render_note(org, item)

    print("\n".join(org))
