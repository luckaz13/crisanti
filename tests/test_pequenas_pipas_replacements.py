import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from tools.acervo.sync_artist_revisions import publish_pipas


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ["10.jpg", "03.jpg", "04.jpg", "pequenas-pipas-4.jpeg", "01.jpg", "02.jpg"]


class PequenasPipasReplacementTests(unittest.TestCase):
    def test_portada_uses_five_replacements_and_preserves_fourth_legacy_composition(self):
        for page in ("index.html", "es/index.html"):
            with self.subTest(page=page):
                soup = BeautifulSoup((ROOT / page).read_text(encoding="utf-8"), "html.parser")
                cards = soup.select('[data-series="pequenas-pipas"] img.obra-img')
                self.assertEqual(6, len(cards))
                self.assertEqual(EXPECTED, [Path(img["src"]).name for img in cards])

    def test_publish_pipas_creates_only_missing_published_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "img" / "Pequeñas Pipas"
            source_root.mkdir(parents=True)
            for name in ("01", "02", "03", "04", "10"):
                (source_root / f"{name}.jpg").write_bytes(f"pipas-{name}".encode())

            created = publish_pipas(root)

            self.assertEqual(
                [root / "img" / "images" / "Pequeñas Pipas" / f"{name}.jpg"
                 for name in ("01", "02", "03", "04", "10")],
                created,
            )

    def test_publish_pipas_accepts_identical_files_and_rejects_divergent_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "img" / "Pequeñas Pipas"
            destination_root = root / "img" / "images" / "Pequeñas Pipas"
            source_root.mkdir(parents=True)
            destination_root.mkdir(parents=True)
            for name in ("01", "02", "03", "04", "10"):
                payload = f"pipas-{name}".encode()
                (source_root / f"{name}.jpg").write_bytes(payload)
                (destination_root / f"{name}.jpg").write_bytes(payload)

            self.assertEqual([], publish_pipas(root))
            (destination_root / "03.jpg").write_bytes(b"different")
            with self.assertRaises(FileExistsError):
                publish_pipas(root)

    def test_publish_pipas_rejects_broken_destination_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "img" / "Pequeñas Pipas"
            destination_root = root / "img" / "images" / "Pequeñas Pipas"
            source_root.mkdir(parents=True)
            destination_root.mkdir(parents=True)
            for name in ("01", "02", "03", "04", "10"):
                (source_root / f"{name}.jpg").write_bytes(f"pipas-{name}".encode())
            outside = root / "outside.jpg"
            (destination_root / "01.jpg").symlink_to(outside)

            with self.assertRaises(FileExistsError):
                publish_pipas(root)
            self.assertFalse(outside.exists())


if __name__ == "__main__":
    unittest.main()
