"""CLI for Snipd."""

from argparse import ArgumentParser

from . import converter


def cli() -> None:
    p = ArgumentParser()
    p.add_argument("snipd_export", nargs="?")
    p.add_argument("--output-format", "-f", choices=("org", "html"), default="org")
    args = p.parse_args()

    with open(args.snipd_export) as f:
        md = f.read()

    output = converter.convert(md, args.output_format)
    print(output)


if __name__ == "__main__":
    raise SystemExit(cli())
