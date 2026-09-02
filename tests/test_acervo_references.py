import tempfile
import unittest
from pathlib import Path

from tools.acervo.audit_references import audit_files
from tools.acervo.migrate_references import migrate_html


class ReferenceAuditTests(unittest.TestCase):
    def test_migrates_hash_matched_asset_and_legacy_fallback(self):
        manifest = {
            "assets": [
                {
                    "path": "img/Ensayos/Obra/01.jpg",
                    "published_matches": ["images/old/current.jpg"],
                }
            ]
        }
        html = '<img src="images/old/current.jpg"><img src="images/old/legacy.jpg">'

        migrated = migrate_html(html, manifest, spanish=False)

        self.assertIn('src="img/images/Ensayos/Obra/01.jpg"', migrated)
        self.assertIn('src="img/images/legacy/old/legacy.jpg"', migrated)

    def test_migrates_spanish_paths_with_parent_prefix(self):
        html = '<img src="../images/hero.jpg">'

        migrated = migrate_html(html, {"assets": []}, spanish=True)

        self.assertEqual('<img src="../img/images/legacy/hero.jpg">', migrated)

    def test_reports_legacy_images_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "index.html"
            page.write_text('<img src="images/old.jpg">', encoding="utf-8")

            report = audit_files(root, [page])

            self.assertEqual(["index.html: images/old.jpg"], report.legacy_references)

    def test_audits_social_image_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "index.html"
            page.write_text('<meta property="og:image" content="images/hero.jpg">', encoding="utf-8")

            report = audit_files(root, [page])

            self.assertEqual(["index.html: images/hero.jpg"], report.legacy_references)

    def test_accepts_existing_published_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asset = root / "img/images/current.jpg"
            asset.parent.mkdir(parents=True)
            asset.write_bytes(b"image")
            page = root / "index.html"
            page.write_text('<img src="img/images/current.jpg">', encoding="utf-8")

            report = audit_files(root, [page])

            self.assertEqual([], report.legacy_references)
            self.assertEqual([], report.missing_assets)

    def test_resolves_spanish_parent_relative_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asset = root / "img/images/current.jpg"
            asset.parent.mkdir(parents=True)
            asset.write_bytes(b"image")
            page = root / "es/index.html"
            page.parent.mkdir()
            page.write_text('<img src="../img/images/current.jpg">', encoding="utf-8")

            report = audit_files(root, [page])

            self.assertEqual([], report.missing_assets)

    def test_reports_missing_local_asset_but_ignores_external_url(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "index.html"
            page.write_text(
                '<img src="img/images/missing.jpg"><a href="https://example.com">x</a>',
                encoding="utf-8",
            )

            report = audit_files(root, [page])

            self.assertEqual(["index.html: img/images/missing.jpg"], report.missing_assets)

    def test_audits_supported_files_within_a_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "js"
            scripts.mkdir()
            (scripts / "gallery.js").write_text(
                '<img src="../img/images/current.jpg">', encoding="utf-8"
            )
            asset = root / "img/images/current.jpg"
            asset.parent.mkdir(parents=True)
            asset.write_bytes(b"image")

            report = audit_files(root, [scripts])

            self.assertEqual([], report.legacy_references)
            self.assertEqual([], report.missing_assets)


if __name__ == "__main__":
    unittest.main()
