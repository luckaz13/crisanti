#!/usr/bin/env python3
"""Materialize reviewed current and legacy-in-use media in img/images."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__:
    from .inventory import sha256_file
else:
    from inventory import sha256_file


class PublishCollision(RuntimeError):
    pass


@dataclass
class PublishReport:
    planned: int = 0
    to_copy: int = 0
    copied: int = 0
    verified: int = 0


def _operations(
    manifest: dict[str, Any], source_root: Path, legacy_root: Path, output_root: Path
) -> list[tuple[Path, Path, str]]:
    operations = []
    for asset in manifest.get("assets", []):
        if asset["classification"] not in {"atual", "novo", "conflito"}:
            continue
        relative = Path(asset["path"]).relative_to("img")
        operations.append((source_root / relative, output_root / relative, asset["sha256"]))
    for asset in manifest.get("legacy", []):
        if asset["classification"] != "legado-em-uso":
            continue
        relative = Path(asset["path"]).relative_to("images")
        operations.append(
            (legacy_root / relative, output_root / "legacy" / relative, asset["sha256"])
        )
    return operations


def publish_manifest(
    manifest: dict[str, Any],
    source_root: Path,
    legacy_root: Path,
    output_root: Path,
    *,
    dry_run: bool,
) -> PublishReport:
    report = PublishReport()
    for source, destination, expected_hash in _operations(
        manifest, source_root, legacy_root, output_root
    ):
        report.planned += 1
        if not source.is_file():
            raise FileNotFoundError(source)
        if sha256_file(source) != expected_hash:
            raise ValueError(f"source checksum mismatch: {source}")
        if destination.exists():
            if sha256_file(destination) != expected_hash:
                raise PublishCollision(f"different bytes already exist: {destination}")
            report.verified += 1
            continue
        report.to_copy += 1
        if dry_run:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        if sha256_file(destination) != expected_hash:
            raise ValueError(f"destination checksum mismatch: {destination}")
        report.copied += 1
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    report = publish_manifest(
        manifest, args.source, args.legacy, args.output, dry_run=args.dry_run
    )
    print(json.dumps(report.__dict__, sort_keys=True))


if __name__ == "__main__":
    main()
