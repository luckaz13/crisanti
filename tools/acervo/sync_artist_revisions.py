#!/usr/bin/env python3
"""Synchronize the approved artist revisions from the fixed source archives."""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile


PRIMARY_ARCHIVE = "drive-download-20260824T065754Z-1-001.zip"
PIPAS_ARCHIVE = "Pequeñas Pipas-20260901T011313Z-1-001.zip"

PRIMARY_MEMBERS = {
    "Seda/SEDA 2024/04.jpg": "img/Seda/SEDA 2024/04.jpg",
    "Seda/SEDA 2024/07.jpg": "img/Seda/SEDA 2024/07.jpg",
    "Seda/SEDA 2024/14.jpg": "img/Seda/SEDA 2024/14.jpg",
}
PIPAS_MEMBERS = {
    f"Pequeñas Pipas/{name}.jpg": f"img/Pequeñas Pipas/{name}.jpg"
    for name in ("01", "02", "03", "04", "10")
}
APPROVED_DESTINATIONS = frozenset((*PRIMARY_MEMBERS.values(), *PIPAS_MEMBERS.values()))


@dataclass(frozen=True)
class SyncAction:
    source_archive: str
    member: str
    destination: Path
    sha256: str


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _validate_destination(destination: Path, root: Path | None = None) -> Path:
    """Return a resolved allowlisted destination or raise ``ValueError``."""
    resolved = destination.resolve()
    if root is not None:
        img_root = (root / "img").resolve()
        try:
            relative = resolved.relative_to(img_root)
        except ValueError as error:
            raise ValueError(f"destination outside img/: {destination}") from error
        relative_name = Path("img", relative).as_posix()
    else:
        # Actions carry no root separately. Recover the ``img`` component only
        # for validating hand-built actions passed to apply_sync_plan.
        try:
            img_index = len(resolved.parts) - 1 - resolved.parts[::-1].index("img")
        except ValueError as error:
            raise ValueError(f"destination outside img/: {destination}") from error
        relative_name = Path("img", *resolved.parts[img_index + 1 :]).as_posix()

    if "images" in resolved.parts or relative_name not in APPROVED_DESTINATIONS:
        raise ValueError(f"destination is not approved: {destination}")
    return resolved


def build_sync_plan(root: Path) -> list[SyncAction]:
    root = root.resolve()
    plan: list[SyncAction] = []
    for archive_name, members in (
        (PRIMARY_ARCHIVE, PRIMARY_MEMBERS),
        (PIPAS_ARCHIVE, PIPAS_MEMBERS),
    ):
        archive_path = root / archive_name
        if not archive_path.is_file():
            raise FileNotFoundError(f"source archive not found: {archive_path}")
        with ZipFile(archive_path) as archive:
            for member, destination_name in members.items():
                payload = archive.read(member)
                destination = _validate_destination(root / destination_name, root)
                plan.append(
                    SyncAction(
                        source_archive=str(archive_path),
                        member=member,
                        destination=destination,
                        sha256=_sha256(payload),
                    )
                )
    return plan


def apply_sync_plan(actions: list[SyncAction], *, dry_run: bool) -> list[Path]:
    written: list[Path] = []
    for action in actions:
        destination = _validate_destination(action.destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not dry_run:
            with ZipFile(action.source_archive) as archive:
                payload = archive.read(action.member)
            if _sha256(payload) != action.sha256:
                raise ValueError(f"hash changed while reading {action.member}")
            destination.write_bytes(payload)
            written.append(destination)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    actions = build_sync_plan(args.root)
    for action in actions:
        print(action.destination.relative_to(args.root.resolve()).as_posix())
    apply_sync_plan(actions, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
