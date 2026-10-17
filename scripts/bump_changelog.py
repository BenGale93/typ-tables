"""Promote the changelog's Unreleased section to a released version."""  # noqa: INP001

# Used by the `just release` recipe. Renaming the section and committing it
# before tagging lets the release workflow build the GitHub release notes from
# the tagged version, and keeps `docs/changelog.md` in sync.

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
UNRELEASED = "## Unreleased"
HEADING_RE = re.compile(r"^## .*$", re.MULTILINE)


def bump(version: str, date: str, changelog: Path = CHANGELOG) -> None:
    """Promote `version` in `changelog`, dated `date`.

    Raises:
        SystemExit: If `version` already has a section, or there is no version
            heading to release above.
    """
    text = changelog.read_text()
    if re.search(rf"^## {re.escape(version)}(?:\s|$)", text, re.MULTILINE):
        msg = f"{changelog.name} already has a section for {version}"
        raise SystemExit(msg)

    section = f"## {version} - {date}"
    if UNRELEASED in text:
        text = text.replace(UNRELEASED, f"{UNRELEASED}\n\n{section}", 1)
    else:
        heading = HEADING_RE.search(text)
        if heading is None:
            msg = f"{changelog.name} has no version heading to release above"
            raise SystemExit(msg)
        text = f"{text[: heading.start()]}{UNRELEASED}\n\n{section}\n\n{text[heading.start() :]}"

    changelog.write_text(text)


def main() -> None:
    """Run the changelog bump from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="version to release, for example 0.4.0")
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="release date in YYYY-MM-DD (defaults to today)",
    )
    args = parser.parse_args()
    if not VERSION_RE.match(args.version):
        sys.exit(f"invalid version {args.version!r}, expected X.Y.Z")
    bump(args.version, args.date)


if __name__ == "__main__":
    main()
