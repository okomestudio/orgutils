"""CLI for Org Zotero exporter."""
from argparse import ArgumentParser

from .exporters import export_to_org, list_items


def cli():  # noqa
    p = ArgumentParser(description=__doc__)
    subparsers = p.add_subparsers(help="subparser help")

    p_extract = subparsers.add_parser("extract", help="extract stuff")
    p_extract.add_argument("id", help="item ID")
    p_extract.set_defaults(func=export_to_org)

    p_list = subparsers.add_parser("list", help="list stuff")
    p_list.set_defaults(func=list_items)

    args = p.parse_args()
    args = vars(args)
    func = args.pop("func")
    func(**args)


if __name__ == "__main__":
    raise SystemExit(cli())
