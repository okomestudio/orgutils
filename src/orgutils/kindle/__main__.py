"""CLI for Org Kindle exporter."""
from argparse import ArgumentParser
from .exporters import export_to_org


def cli():  # noqa
    p = ArgumentParser(description=__doc__)
    p.add_argument("dump", help="Bookcision JSON dump")
    p.add_argument("--lang", "-l", choices=("en", "ja"), default="en", help="Language")

    args = p.parse_args()

    export_to_org(**vars(args))


if __name__ == "__main__":
    raise SystemExit(cli())
