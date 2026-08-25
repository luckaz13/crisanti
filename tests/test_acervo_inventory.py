import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tools.acervo.inventory import natural_key, scan_media, sha256_file


class NaturalKeyTests(unittest.TestCase):
    def test_sorts_numbered_filenames_naturally(self):
        names = ["10.jpg", "02.jpg", "1.jpg", "00.jpg"]

        self.assertEqual(
            sorted(names, key=natural_key),
            ["00.jpg", "1.jpg", "02.jpg", "10.jpg"],
        )


class MediaInventoryTests(unittest.TestCase):
    def test_scans_media_with_stable_metadata_and_accents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            series = root / "Ensayos" / "Emulsión"
            series.mkdir(parents=True)
            image_path = series / "02.jpg"
            Image.new("RGB", (13, 7), "white").save(image_path)

            records = scan_media(root)

            self.assertEqual(len(records), 1)
            record = records[0]
            self.assertEqual(record.path, "Ensayos/Emulsión/02.jpg")
            self.assertEqual(record.section, "Ensayos")
            self.assertEqual(record.series, "Emulsión")
            self.assertEqual(record.filename, "02.jpg")
            self.assertEqual(record.order, 2)
            self.assertEqual((record.width, record.height), (13, 7))
            self.assertEqual(record.sha256, hashlib.sha256(image_path.read_bytes()).hexdigest())

    def test_identical_bytes_have_identical_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.jpg"
            second = root / "second.jpg"
            payload = b"same-artwork"
            first.write_bytes(payload)
            second.write_bytes(payload)

            self.assertEqual(sha256_file(first), sha256_file(second))


if __name__ == "__main__":
    unittest.main()
