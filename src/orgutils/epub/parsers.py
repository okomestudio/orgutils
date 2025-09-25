from collections import defaultdict

from ebooklib import epub
from lxml import etree

# NOTE: Page information is embedded in the element like this:
#
# <span id="p144" aria-label=" page 144. " epub:type="pagebreak" role="doc-pagebreak"/>


def parse_ebook_structure(epub_path):
    book = epub.read_epub(epub_path)
    namespaces = {
        "xhtml": "http://www.w3.org/1999/xhtml",
        "epub": "http://www.idpf.org/2007/ops",
    }

    current_page: str = None
    book_items = defaultdict(list)

    for item in book.get_items():
        if item.get_name().endswith((".html", ".xhtml")):
            content = item.get_content()
            try:
                root = etree.fromstring(content)

                for elem in root.xpath(
                    '//xhtml:h1 | //xhtml:h2 | //xhtml:h3 | //xhtml:span[@epub:type="pagebreak"] ',
                    namespaces=namespaces,
                ):
                    if etree.QName(elem).localname == "span":
                        current_page = elem.attrib.get("id")[1:]
                        _ = book_items[current_page]
                    else:
                        title = (
                            elem.xpath("string()").strip()
                            if elem.xpath("string()").strip()
                            else ""
                        )
                        tag = elem.tag.split("}")[-1]

                        subelems = elem.xpath(
                            './/xhtml:span[@epub:type="pagebreak"]',
                            namespaces=namespaces,
                        )
                        if subelems and etree.QName(subelems[0]).localname == "span":
                            current_page = subelems[0].attrib.get("id")[1:]

                        book_items[current_page].append((tag, title))
            except etree.XMLSyntaxError:
                raise

    return book_items
