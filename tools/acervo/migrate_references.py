#!/usr/bin/env python3
"""Migrate active legacy image URLs to the consolidated img/images tree."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _current_paths(manifest: dict[str, Any]) -> dict[str, str]:
    paths: dict[str, str] = {}
    for asset in manifest.get("assets", []):
        destination = "img/images/" + asset["path"].removeprefix("img/")
        for old_path in asset.get("published_matches", []):
            paths[old_path] = destination
    return paths


def migrate_html(html: str, manifest: dict[str, Any], *, spanish: bool) -> str:
    old_prefix = "../images/" if spanish else "images/"
    new_prefix = "../" if spanish else ""
    current_paths = _current_paths(manifest)
    pattern = re.compile(rf'((?:src|href)=["\']){re.escape(old_prefix)}([^"\']+)(["\'])')

    def replace(match: re.Match[str]) -> str:
        old_path = "images/" + match.group(2)
        destination = current_paths.get(old_path, "img/images/legacy/" + match.group(2))
        return match.group(1) + new_prefix + destination + match.group(3)

    return pattern.sub(replace, html)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--pt", type=Path, required=True)
    parser.add_argument("--es", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.pt.write_text(migrate_html(args.pt.read_text(encoding="utf-8"), manifest, spanish=False), encoding="utf-8")
    args.es.write_text(migrate_html(args.es.read_text(encoding="utf-8"), manifest, spanish=True), encoding="utf-8")


if __name__ == "__main__":
    main()
