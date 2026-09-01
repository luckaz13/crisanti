import hashlib
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from zipfile import ZipFile

from tools.acervo.sync_artist_revisions import (
    PRIMARY_ARCHIVE,
    PRIMARY_MEMBERS,
    PIPAS_ARCHIVE,
    PIPAS_MEMBERS,
    apply_sync_plan,
    build_sync_plan,
)


ROOT = Path(__file__).resolve().parents[1]


def make_fixture(root: Path) -> None:
    (root / "img").mkdir(parents=True)
    with ZipFile(root / PRIMARY_ARCHIVE, "w") as archive:
        for member in PRIMARY_MEMBERS:
            archive.writestr(member, f"primary:{member}".encode())
    with ZipFile(root / PIPAS_ARCHIVE, "w") as archive:
        for member in PIPAS_MEMBERS:
            archive.writestr(member, f"pipas:{member}".encode())


class ArtistRevisionSyncTests(unittest.TestCase):
    def test_plan_contains_only_eight_approved_replacements(self):
        actions = build_sync_plan(ROOT)

        self.assertEqual(8, len(actions))
        self.assertEqual(
            {
                "img/Seda/SEDA 2024/04.jpg",
                "img/Seda/SEDA 2024/07.jpg",
                "img/Seda/SEDA 2024/14.jpg",
                "img/Pequeñas Pipas/01.jpg",
                "img/Pequeñas Pipas/02.jpg",
                "img/Pequeñas Pipas/03.jpg",
                "img/Pequeñas Pipas/04.jpg",
                "img/Pequeñas Pipas/10.jpg",
            },
            {a.destination.relative_to(ROOT).as_posix() for a in actions},
        )

    def test_plan_never_targets_backup_trees(self):
        for action in build_sync_plan(ROOT):
            relative = action.destination.relative_to(ROOT).as_posix()
            self.assertFalse(relative.startswith("images/"))
            self.assertFalse(relative.startswith("img/images/"))

    def test_dry_run_does_not_create_directories_or_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_fixture(root)
            before = set(root.rglob("*"))

            self.assertEqual([], apply_sync_plan(build_sync_plan(root), dry_run=True))

            self.assertEqual(before, set(root.rglob("*")))

    def test_apply_rejects_destination_from_a_different_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_fixture(root)
            action = build_sync_plan(root)[0]
            external = root / "other" / "img" / "Seda" / "SEDA 2024" / "04.jpg"

            with self.assertRaises(ValueError):
                apply_sync_plan([replace(action, destination=external)], dry_run=True)

    def test_apply_rejects_repository_backup_trees(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_fixture(root)
            action = build_sync_plan(root)[0]
            relative_target = Path("Seda/SEDA 2024/04.jpg")

            for backup in (root / "images", root / "img" / "images"):
                destination = backup / relative_target
                with self.subTest(destination=destination), self.assertRaises(ValueError):
                    apply_sync_plan([replace(action, destination=destination)], dry_run=True)

    def test_apply_rejects_hash_changed_after_planning(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_fixture(root)
            action = build_sync_plan(root)[0]

            with self.assertRaises(ValueError):
                apply_sync_plan([replace(action, sha256="0" * 64)], dry_run=False)

    def test_apply_rejects_arbitrary_archive_and_member(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_fixture(root)
            action = build_sync_plan(root)[0]
            payload = b"arbitrary"
            arbitrary_archive = root / "arbitrary.zip"
            with ZipFile(arbitrary_archive, "w") as archive:
                archive.writestr(action.member, payload)

            with self.assertRaises(ValueError):
                apply_sync_plan(
                    [
                        replace(
                            action,
                            source_archive=str(arbitrary_archive),
                            sha256=hashlib.sha256(payload).hexdigest(),
                        )
                    ],
                    dry_run=False,
                )

            with ZipFile(root / PRIMARY_ARCHIVE, "a") as archive:
                archive.writestr("arbitrary/member.jpg", payload)
            with self.assertRaises(ValueError):
                apply_sync_plan(
                    [
                        replace(
                            action,
                            member="arbitrary/member.jpg",
                            sha256=hashlib.sha256(payload).hexdigest(),
                        )
                    ],
                    dry_run=False,
                )

    def test_root_with_images_ancestor_is_not_a_backup_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "images" / "project"
            root.mkdir(parents=True)
            make_fixture(root)

            self.assertEqual([], apply_sync_plan(build_sync_plan(root), dry_run=True))


if __name__ == "__main__":
    unittest.main()
