"""Kindle highlights to Org converter.

Use Bookcision to JSON export Kindle highlights and notes in Amazon
Cloud Reader.
"""
import json
import re
from collections import namedtuple
from typing import List

from .. import utils
from ..org import structs

KindleHighlight = namedtuple("KindleHighlight", ("location", "data"))


def export_to_org(dump: str, lang: str) -> None:
    """Take Bookcision JSON dump and export as Org."""
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
    sorted_items = [KindleHighlight(x["location"]["value"], x) for x in highlights]

    base_heading_depth = 1
    sorted_items = sorted(
        sorted_items,
        key=lambda item: (
            item.location,
            (
                # Make header lines come earliest if they are on the
                # same location:
                -1
                if (item.data.get("note") or "").startswith("h")
                or (item.data.get("note") or "").startswith("H")
                else 0
            ),
        ),
    )

    # Org tree for vocab
    org_vocab: List[structs.OrgObject] = []
    org_vocab.append(structs.Heading("Vocab", 1, {}))

    # Org tree for notes & highlights
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

    # Parse items in the order of location
    idx = 0
    while idx < len(sorted_items):
        item = sorted_items[idx]

        # Vocab
        m = re.match(r"^(?:[vV]ocab|語彙|表現)\s*(|.*)$", item.data.get("note") or "")
        if m:
            org_vocab.append(
                structs.Heading(
                    preprocess(m.group(1) or item.data["text"]),
                    1 + base_heading_depth,
                    {"kindle_loc": item.location},
                )
            )
            org_vocab.append(
                structs.QuoteBlock(
                    f"{ preprocess(item.data['text']) } (loc. { item.location })"
                )
            )
            idx += 1
            continue

        # Header
        m = re.match(r"^[hH](\d+)(|\s+(.*))$", item.data.get("note") or "")
        if m:
            heading_depth = int(m.group(1))

            text = m.group(3) or item.data["text"]
            if not text:
                # For the most part, missing text here means the note
                # and highlight locations do not match, or a separate
                # note item exists at the same location. Look for the
                # closest highlight text that looks like a heading.
                items = sorted(
                    [
                        (
                            abs(sorted_items[idx + 1].location - item.location),
                            len(sorted_items[idx + 1].data["text"]),
                            sorted_items[idx + 1],
                        ),
                        (
                            abs(sorted_items[idx - 1].location - item.location),
                            len(sorted_items[idx - 1].data["text"]),
                            sorted_items[idx - 1],
                        ),
                    ]
                )
                if items[0][0] <= 1:
                    text = items[0][2].data["text"]
                else:
                    text = "--MISSING--"

            org.append(
                structs.Heading(
                    preprocess(text),
                    heading_depth + base_heading_depth,
                    {"kindle_loc": item.location},
                )
            )
            idx += 1
            continue

        # Quote
        org.append(
            structs.QuoteBlock(
                f"{ preprocess(item.data['text']) } (loc. { item.location })"
            )
        )
        if item.data.get("note"):
            org.append(structs.Paragraph(item.data["note"]))
        idx += 1

    # render org doc
    print(structs.dumps(org))
    print(structs.dumps(org_vocab))
