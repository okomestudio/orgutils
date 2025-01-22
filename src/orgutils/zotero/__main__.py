"""CLI for Org Zotero exporter."""

from argparse import ArgumentParser

from .docs import list_docs
from .exporters import export_to_org
from .items import list_items


def cli():  # noqa
    p = ArgumentParser(description=__doc__)
    subparsers = p.add_subparsers(help="subcommands")

    p_extract = subparsers.add_parser("extract", help="extract stuff")
    p_extract.add_argument("id", help="item ID")
    p_extract.add_argument(
        "--lang", "-l", choices=("en", "ja"), default="en", help="Language"
    )
    p_extract.set_defaults(func=export_to_org)

    p_docs = subparsers.add_parser("docs", help="docs")
    p_docs_list = p_docs.add_subparsers(help="docs subcommands")
    p_docs_list = p_docs_list.add_parser("list", help="list docs")
    p_docs_list.set_defaults(func=list_docs)

    p_items = subparsers.add_parser("items", help="items")
    p_items_list = p_items.add_subparsers(help="items subcommands")
    p_items_list = p_items_list.add_parser("list", help="list items")
    p_items_list.set_defaults(func=list_items)

    args = p.parse_args()
    args = vars(args)
    func = args.pop("func")
    func(**args)


if __name__ == "__main__":
    raise SystemExit(cli())
