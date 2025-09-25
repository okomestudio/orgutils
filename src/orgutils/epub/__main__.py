"""CLI for .epub exporter."""

from argparse import ArgumentParser

from .parsers import parse_ebook_structure


def parse_book_structure(epub_path):
    book_items = parse_ebook_structure(epub_path)
    for page, book_item in book_items.items():
        print(page, book_item)


def cli() -> None:
    """CLI entry point."""
    p = ArgumentParser(description=__doc__)
    p.add_argument("epub", help=".epub file")

    args = p.parse_args()

    parse_book_structure(args.epub)


if __name__ == "__main__":
    raise SystemExit(cli())
