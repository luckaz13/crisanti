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
PIPAS_PUBLISHED_DESTINATIONS = {
    f"{name}.jpg": f"img/images/Pequeñas Pipas/{name}.jpg"
    for name in ("01", "02", "03", "04", "10")
}
APPROVED_DESTINATIONS = frozenset((*PRIMARY_MEMBERS.values(), *PIPAS_MEMBERS.values()))
ARCHIVE_MEMBERS = {
    PRIMARY_ARCHIVE: PRIMARY_MEMBERS,
    PIPAS_ARCHIVE: PIPAS_MEMBERS,
}


@dataclass(frozen=True)
class SyncAction:
    source_archive: str
    member: str
    destination: Path
    sha256: str


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_under(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def _validate_destination(destination: Path, root: Path, expected_name: str) -> Path:
    """Return an exact, resolved allowlisted destination or raise ``ValueError``."""
    resolved = destination.resolve()
    root = root.resolve()
    img_root = (root / "img").resolve()
    try:
        img_root.relative_to(root)
        resolved.relative_to(img_root)
    except ValueError as error:
        raise ValueError(f"destination outside img/: {destination}") from error

    # Only these two repository-relative backup trees are forbidden. An
    # unrelated ancestor directory may legitimately be named ``images``.
    for backup_root in (root / "images", root / "img" / "images"):
        if _is_under(resolved, backup_root.resolve()):
            raise ValueError(f"destination is a backup tree: {destination}")

    if expected_name not in APPROVED_DESTINATIONS:
        raise ValueError(f"destination is not approved: {destination}")
    expected = (root / expected_name).resolve()
    if resolved != expected:
        raise ValueError(f"destination is not approved: {destination}")
    return resolved


def _archive_spec(source_archive: str) -> tuple[Path, Path, dict[str, str]]:
    """Validate a fixed archive path and return its logical root and map."""
    source = Path(source_archive)
    resolved_source = source.resolve()
    members = ARCHIVE_MEMBERS.get(source.name)
    if members is None or not source.is_file() or resolved_source.name != source.name:
        raise ValueError(f"source archive is not approved: {source_archive}")

    # The worktree exposes the fixed ZIPs as symlinks to shared immutable
    # copies. Use the symlink's repository parent for destinations; for a
    # regular ZIP this is exactly Path(source_archive).resolve().parent.
    root = source.parent.resolve() if source.is_symlink() else resolved_source.parent
    return source, root, members


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
                destination = _validate_destination(
                    root / destination_name, root, destination_name
                )
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
        source_archive, root, members = _archive_spec(action.source_archive)
        expected_name = members.get(action.member)
        if expected_name is None:
            raise ValueError(f"archive member is not approved: {action.member}")
        destination = _validate_destination(action.destination, root, expected_name)
        with ZipFile(source_archive) as archive:
            payload = archive.read(action.member)
        expected_sha256 = _sha256(payload)
        if action.sha256 != expected_sha256:
            raise ValueError(f"hash changed while reading {action.member}")
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
            written.append(destination)
    return written


def publish_pipas(root: Path) -> list[Path]:
    """Publish the approved Pequeñas Pipas source files without overwriting.

    A destination is created only when absent. Existing destinations are
    accepted when their bytes match the source and rejected otherwise.
    """
    root = root.resolve()
    written: list[Path] = []
    for name, destination_name in PIPAS_PUBLISHED_DESTINATIONS.items():
        source = root / "img" / "Pequeñas Pipas" / name
        destination = root / destination_name
        if not source.is_file():
            raise FileNotFoundError(source)

        payload = source.read_bytes()
        source_sha256 = _sha256(payload)
        if destination.exists() or destination.is_symlink():
            if not destination.is_file() or _sha256(destination.read_bytes()) != source_sha256:
                raise FileExistsError(f"different bytes already exist: {destination}")
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        written.append(destination)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--publish-pipas", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.publish_pipas:
        for destination in publish_pipas(args.root):
            print(destination.relative_to(args.root.resolve()).as_posix())
        return

    actions = build_sync_plan(args.root)
    for action in actions:
        print(action.destination.relative_to(args.root.resolve()).as_posix())
    apply_sync_plan(actions, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
