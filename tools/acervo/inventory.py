#!/usr/bin/env python3
"""Create a deterministic inventory of the artist archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image


MEDIA_EXTENSIONS = {
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}


def natural_key(name: str) -> tuple[tuple[int, object], ...]:
    """Return a stable key that sorts digit groups numerically."""
    parts = re.split(r"(\d+)", name.casefold())
    return tuple((0, int(part)) if part.isdigit() else (1, part) for part in parts)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def numeric_order(filename: str) -> int | None:
    match = re.match(r"^(\d+)", filename)
    return int(match.group(1)) if match else None


@dataclass(frozen=True)
class MediaRecord:
    path: str
    section: str
    series: str
    filename: str
    order: int | None
    sha256: str
    width: int
    height: int


def scan_media(root: Path) -> list[MediaRecord]:
    root = root.resolve()
    paths = sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.casefold() in MEDIA_EXTENSIONS
        ),
        key=lambda path: natural_key(path.relative_to(root).as_posix()),
    )
    records: list[MediaRecord] = []
    for path in paths:
        relative = path.relative_to(root)
        parent_parts = relative.parts[:-1]
        section = parent_parts[0] if parent_parts else ""
        series = "/".join(parent_parts[1:]) if len(parent_parts) > 1 else ""
        with Image.open(path) as image:
            width, height = image.size
        records.append(
            MediaRecord(
                path=relative.as_posix(),
                section=section,
                series=series,
                filename=path.name,
                order=numeric_order(path.name),
                sha256=sha256_file(path),
                width=width,
                height=height,
            )
        )
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--published", type=Path)
    parser.add_argument("--html", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_records = scan_media(args.source)
    payload: dict[str, object] = {
        "schema_version": 1,
        "source_root": "img",
        "source": [asdict(record) | {"path": f"img/{record.path}"} for record in source_records],
    }
    if args.published:
        payload["published_root"] = args.published.as_posix()
        payload["published"] = [asdict(record) for record in scan_media(args.published)]
    if args.html:
        payload["html"] = args.html.as_posix()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
