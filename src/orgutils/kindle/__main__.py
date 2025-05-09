"""CLI for Org Kindle exporter."""

from argparse import ArgumentParser

from .converters import convert_html_to_org, export_to_org


def cli() -> None:
    """CLI entry point."""
    p = ArgumentParser(description=__doc__)
    p.add_argument(
        "dump", help="JSON (via Bookcision) or HTML (via Kindle) export file"
    )
    p.add_argument(
        "--format",
        "-f",
        choices=("json", "html"),
        default="json",
        help="Export file format (default: json)",
    )
    p.add_argument("--lang", "-l", choices=("en", "ja"), default="en", help="Language")

    args = p.parse_args()

    {
        "json": export_to_org,
        "html": convert_html_to_org,
    }[args.format](**vars(args))


if __name__ == "__main__":
    raise SystemExit(cli())  # type: ignore
