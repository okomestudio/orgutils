"""Utility."""
import re
import xml.dom.minidom
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element


def dumps_xml(tree: Element, indent: int = 2) -> str:
    """Dump XML as string."""
    dom = xml.dom.minidom.parseString(ET.tostring(tree))
    return dom.toprettyxml(indent=" " * 2)


def remove_whitespaces_between_zenkaku(s: str) -> str:
    """Remove space(s) between zenkaku characters."""
    s = re.sub(r"(?<=[^\x01-\x7E])([^\S\n\r]+)(?=[^\x01-\x7E])", "", s)
    return s
