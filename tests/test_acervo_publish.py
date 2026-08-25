import hashlib
import tempfile
import unittest
from pathlib import Path

from tools.acervo.publish_assets import PublishCollision, publish_manifest


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class AssetPublishingTests(unittest.TestCase):
    def test_dry_run_does_not_copy_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "01.jpg").write_bytes(b"current")
            manifest = {"assets": [{"path": "img/01.jpg", "sha256": digest(b"current"), "classification": "novo"}], "legacy": []}

            report = publish_manifest(manifest, source, root / "legacy", root / "output", dry_run=True)

            self.assertEqual(report.to_copy, 1)
            self.assertFalse((root / "output" / "01.jpg").exists())

    def test_refuses_different_bytes_at_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            output = root / "output"
            source.mkdir()
            output.mkdir()
            (source / "01.jpg").write_bytes(b"current")
            (output / "01.jpg").write_bytes(b"wrong")
            manifest = {"assets": [{"path": "img/01.jpg", "sha256": digest(b"current"), "classification": "atual"}], "legacy": []}

            with self.assertRaises(PublishCollision):
                publish_manifest(manifest, source, root / "legacy", output, dry_run=False)

    def test_second_run_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "01.jpg").write_bytes(b"current")
            manifest = {"assets": [{"path": "img/01.jpg", "sha256": digest(b"current"), "classification": "atual"}], "legacy": []}

            first = publish_manifest(manifest, source, root / "legacy", root / "output", dry_run=False)
            second = publish_manifest(manifest, source, root / "legacy", root / "output", dry_run=False)

            self.assertEqual(first.copied, 1)
            self.assertEqual(second.copied, 0)
            self.assertEqual(second.verified, 1)


if __name__ == "__main__":
    unittest.main()
