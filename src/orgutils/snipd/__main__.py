"""CLI for Snipd."""

import re
from argparse import ArgumentParser

from . import converter


def cli() -> None:
    p = ArgumentParser()
    p.add_argument("snipd_export")
    p.add_argument("part_no", nargs="?", type=int, default=None)
    p.add_argument("--output-format", "-f", choices=("org", "html"), default="org")
    args = p.parse_args()

    with open(args.snipd_export) as f:
        md = f.read()

    # See if the markdown doc contains multiple top-level sections:
    parts = re.split(r"\n# ", md)
    if len(parts) != 1 and args.part_no is None:
        # If multiple sections exist and no part number is given, list all:
        for i in range(len(parts)):
            header, _ = re.split(r"\n", parts[i], 1)
            print(f"{i}: {header}")
        return
    elif len(parts) == 1:
        args.part_no = 0

    part = parts[args.part_no]
    part = part if part.startswith("# ") else "# " + part

    output = converter.convert(part, args.output_format)
    print(output)


if __name__ == "__main__":
    raise SystemExit(cli())
