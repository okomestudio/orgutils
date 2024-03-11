"""Kindle highlights to Org converter.

Use Bookcision to JSON export Kindle highlights and notes in Amazon
Cloud Reader. Then feed that file to this script to import as Org
file.

TODO: Rewrite in Emacs Lisp.

"""
import json
import re
from typing import List

from .. import utils
from ..org import structs


def export_to_org(dump: str, lang: str) -> None:
    """Take JSON dump and export to Org."""
    with open(dump) as f:
        jd = json.load(f)

    preprocess = (
        utils.remove_whitespaces_between_zenkaku if lang == "ja" else lambda s: s
    )

    title = preprocess(jd["title"])
    authors = jd["authors"]
    asin = jd["asin"]
    highlights = jd["highlights"]

    # Sort items by location
    sorted_items = [(x["location"]["value"], x) for x in highlights]

    base_heading_depth = 1
    sorted_items = sorted(
        sorted_items,
        key=lambda tpl: (
            tpl[0],
            (
                # Make header lines come earliest if they are on the
                # same location:
                -1
                if (tpl[1].get("note") or "").startswith("h")
                or (tpl[1].get("note") or "").startswith("H")
                else 0
            ),
        ),
    )

    # Build org tree for vocab
    org_vocab: List[structs.OrgObject] = []
    org_vocab.append(structs.Heading("Vocab", 1, {}))

    # Build org tree
    org: List[structs.OrgObject] = []
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
        # Header
        m = re.match(r"^[hH](\d+)(|\s+(.*))$", item.get("note") or "")
        if m:
            heading_depth = int(m.group(1))
            org.append(
                structs.Heading(
                    preprocess(m.group(3) or item["text"] or "--MISSING--"),
                    heading_depth + base_heading_depth,
                    {"kindle_loc": item["location"]["value"]},
                )
            )
            continue

        # Vocab
        m = re.match(r"^(?:[vV]ocab|語彙|表現)\s*(|.*)$", item.get("note") or "")
        if m:
            org_vocab.append(
                structs.Heading(
                    preprocess(m.group(1) or item["text"]),
                    1 + base_heading_depth,
                    {"kindle_loc": item["location"]["value"]},
                )
            )
            org_vocab.append(
                structs.QuoteBlock(
                    f"{ preprocess(item['text']) } (loc. { item['location']['value'] })"
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
    print(structs.dumps(org_vocab))
