"""Converter via Pandoc filter."""

import re

import pypandoc
from panflute import (
    Doc,
    Element,
    Header,
    HorizontalRule,
    LineBreak,
    Link,
    Para,
    SoftBreak,
    Space,
    Span,
    Str,
    Strong,
    run_filters,
)

_STACK: list[str] = []


def remove_property_drawer(elem: Element, doc: Doc) -> list[Element] | None:
    """Remove property drawer with CUSTOM_ID from (sub)headings."""
    if isinstance(elem, Header):
        elem.identifier = ""


def replace_linebreak_with_newline(elem: Element, doc: Doc) -> list[Element] | None:
    """Remove <br> rendered as "\\"."""
    if isinstance(elem, LineBreak):
        return [Str("\n")]


def _make_visible_text(elems: list[Element]) -> str:
    strs = []
    for elem in elems:
        if isinstance(elem, Space):
            strs.append(" ")
        elif isinstance(elem, SoftBreak):
            strs.append("\n")
        elif hasattr(elem, "text"):
            strs.append(elem.text)
        elif hasattr(elem, "title"):
            strs.append(elem.title)
        elif isinstance(elem, Link):
            strs.append(_make_visible_text(elem.content[0]))
        elif isinstance(elem, (Strong, Span)):
            strs.append(_make_visible_text(elem.content))
        else:
            raise ValueError(f"Cannot render text: {elem}")
    return "".join(strs)


def remove_paragraph_with_some_text(elem: Element, doc: Doc) -> list[Element] | None:
    """Remove paragraph including some texts."""
    if isinstance(elem, Para):
        s = _make_visible_text(elem.content)
        if (
            (s == "Click to expand")
            or ("Created with" in s and "Take Notes from Podcasts" in s)
            # or ("Thank you for subscribing" in s and "share this episode" in s)
        ):
            return []


def _remove_emoji(s: str) -> str:
    t = re.sub(
        "["
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f700-\U0001f77f"  # alchemical symbols
        "\U0001f780-\U0001f7ff"  # Geometric Shapes Extended
        "\U0001f800-\U0001f8ff"  # Supplemental Arrows-C
        "\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
        "\U0001fa00-\U0001fa6f"  # Chess Symbols
        "\U0001fa70-\U0001faff"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027b0"  # Dingbats
        "\U000024c2-\U0001f251"
        "]+",
        "",
        s,
    )
    return t


def remove_emoji(elem: Element, doc: Doc) -> list[Element] | None:
    """Remove emoji characters from texts."""
    if isinstance(elem, Para) or isinstance(elem, Header):
        content = []
        removed_emoji_only_node = False
        for e in elem.content:
            if isinstance(e, Str):
                text = _remove_emoji(e.text)
                if not text:
                    removed_emoji_only_node = True
                else:
                    removed_emoji_only_node = False
                    content.append(e)
            elif isinstance(e, Space):
                if removed_emoji_only_node:
                    # Eat away a space following a removed emoji
                    removed_emoji_only_node = False
                else:
                    content.append(e)
            else:
                content.append(e)
        elem.content = content


def demote_summary_heading_in_old_dump(elem: Element, doc: Doc) -> list[Element] | None:
    if isinstance(elem, Header):
        first_elem = elem.content[0]
        if isinstance(first_elem, Str):
            if first_elem.text == "Summary":
                elem.level += 1


def remove_horizontal_line(elem: Element, doc: Doc) -> list[Element] | None:
    if isinstance(elem, HorizontalRule):
        return []


def cli(doc: Doc | None = None) -> None | Doc:
    """The CLI entry point."""
    return run_filters(
        [
            remove_property_drawer,
            replace_linebreak_with_newline,
            remove_paragraph_with_some_text,
            remove_emoji,
            remove_horizontal_line,
            demote_summary_heading_in_old_dump,
        ],
        doc=doc,
    )


def _preprocess_md(md: str) -> str:
    # Fix the "Show notes" section
    pattern = "<details>\n<summary>Show notes</summary>\n(.+?)\n</details>"
    m = re.search(pattern, md, re.S)
    if m:
        s = m.group(1)
        s = re.sub("<br/>", "\n\n", s, re.S)
        s = re.sub(">\\s+", "", s, re.S)
        s = re.sub(r"^([0-9]{2}:[0-9]{2}(:[0-9]{2})? .+)", r"- \1", s, flags=re.M)
        md = re.sub(
            pattern,
            "\n## Show notes\n\n__SHOW_NOTES__\n",
            md,
            re.S,
        )
        md = re.sub("__SHOW_NOTES__", s, md)

    return md


def _postprocess_org(org: str) -> str:
    org = re.sub(r"^>( ?(.*))\n", r"\2\n\n", org, flags=re.M)
    org = re.sub(r"^ +(.+)\n", r"\1\n", org, flags=re.M)
    return org


def convert(md: str, output_format: str) -> str:
    """Convert Markdown content to a str doc of given format."""
    # md = _preprocess_md(md)
    html = pypandoc.convert_text(md, "html", format="gfm")
    output = pypandoc.convert_text(
        html,
        output_format,
        format="html",
        extra_args=["--wrap=none"],
        filters=["snipdfilter"],
    )
    if output_format == "org":
        output = _postprocess_org(output)
    return output
