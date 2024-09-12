"""Snipd converter."""
import re
import sys
from typing import Any, List

import markdown
from lxml import etree


def to_html(snipd_export: str, **kwargs: Any) -> str:
    """Convert Snip markdown dump to HTML."""
    with open(snipd_export) as f:
        html = markdown.markdown(f.read())

    dom = etree.HTML(html)

    for elmt in dom.xpath("//a"):
        if "Play snip" in elmt.text:
            elmt.text = elmt.text[2:]

    for elmt in dom.xpath("//h3"):
        if "Summary" in elmt.text:
            elmt.tag = "h4"
            elmt.text = "Summary"

    for elmt in dom.xpath("//h4"):
        if "Transcript" in elmt.text:
            elmt.text = "Transcript"

    for transcript in dom.xpath("//h4[contains(text(), 'Transcript')]"):
        for details in transcript.xpath(".//following-sibling::details[1]"):
            for summary in details.xpath(
                ".//summary[contains(text(), 'Click to expand')]"
            ):
                summary.getparent().remove(summary)

            blockquotes = details.xpath(".//blockquote")
            for blockquote in blockquotes[::-1]:
                transcript.addnext(blockquote)
            details.getparent().remove(details)

    for elmt in dom.xpath("//hr"):
        elmt.getparent().remove(elmt)

    return etree.tostring(dom, pretty_print=True, encoding=str)


def fix_org(**kwargs: Any) -> List[str]:
    """Fix converted Org file."""
    input_data = kwargs.get("snipd_export")
    if input_data:
        input_data = open(input_data)
    else:
        input_data = sys.stdin

    output = []
    for line in input_data:
        # Property drawer
        # line = re.sub(r"^\s+(:[_0-9A-Za-z]+:.*)$", r"\1", line)  # de-indent
        if re.match(r"^\s+(:[_0-9A-Za-z]+:.*)$", line):
            continue

        if "Created with" in line and "Highlight & Take Notes from Podcasts" in line:
            continue

        line = re.sub(r"^Show notes$", "** Show notes", line)
        line = re.sub(r"^> (.*)", r"- \1", line)
        line = re.sub(r"^(- Show notes link: .*)$", r"--------\n\1", line)

        # Remove leading whitespaces
        line = re.sub(r"^\s+(.+)$", r"\1", line)

        # Double backslash converted from <b>
        line = re.sub(r"\\", "", line)

        # Remove emoji
        line = re.sub(
            "["
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+",
            "",
            line,
        )

        output.append(line)

    return output
