"""CLI for Snipd."""
import subprocess
from argparse import ArgumentParser

from . import converter


def main(snipd_export: str, **kwargs) -> None:
    cmd = (
        f"python -m orgutils.snipd --to-html {snipd_export}"
        " | pandoc --wrap=none -f html -t org"
        " | python -m orgutils.snipd --post-process"
    )
    output = subprocess.getoutput(cmd)
    print(output)


def cli():  # noqa
    p = ArgumentParser()
    p.add_argument("snipd_export", nargs="?")
    p.add_argument("--to-html", action="store_true")
    p.add_argument("--post-process", action="store_true")
    args = p.parse_args()

    if not args.to_html and not args.post_process:
        main(**vars(args))
    elif args.to_html:
        output = converter.to_html(**vars(args))
        print(output)
    elif args.post_process:
        output = converter.fix_org(**vars(args))
        print("".join(output))


if __name__ == "__main__":
    raise SystemExit(cli())
