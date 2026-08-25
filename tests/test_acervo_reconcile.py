import subprocess
import sys
import unittest
from pathlib import Path

from tools.acervo.reconcile import reconcile


def media(path, sha, width=100, height=100, section="Seda", series="SEDA", order=1):
    return {
        "path": path,
        "filename": path.rsplit("/", 1)[-1],
        "sha256": sha,
        "width": width,
        "height": height,
        "section": section,
        "series": series,
        "order": order,
    }


class ReconciliationTests(unittest.TestCase):
    def test_cli_can_run_as_a_direct_script(self):
        repository = Path(__file__).resolve().parents[1]

        result = subprocess.run(
            [sys.executable, "tools/acervo/reconcile.py", "--help"],
            cwd=repository,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--inventory", result.stdout)

    def test_classifies_exact_renamed_match_as_current(self):
        source = [media("img/Seda/SEDA/01.jpg", "same")]
        published = [media("galerias/Seda/old-name.jpg", "same")]

        result = reconcile(source, published, set(), [])

        self.assertEqual(result["assets"][0]["classification"], "atual")
        self.assertEqual(result["assets"][0]["published_matches"], ["images/galerias/Seda/old-name.jpg"])

    def test_classifies_unmatched_source_as_new(self):
        result = reconcile([media("img/Seda/SEDA/02.jpg", "new")], [], set(), [])

        self.assertEqual(result["assets"][0]["classification"], "novo")

    def test_preserves_referenced_published_asset_as_legacy_in_use(self):
        published = [media("novas/verde.jpg", "legacy")]

        result = reconcile([], published, {"images/novas/verde.jpg"}, [])

        self.assertEqual(result["legacy"][0]["classification"], "legado-em-uso")

    def test_marks_unreferenced_published_asset_as_replaced(self):
        published = [media("galerias/Seda/unused.jpg", "unused")]

        result = reconcile([], published, set(), [])

        self.assertEqual(result["legacy"][0]["classification"], "substituído")

    def test_marks_ambiguous_non_hash_candidates_as_conflict(self):
        source = [media("img/Seda/SEDA/01.jpg", "source", width=640, height=480)]
        published = [
            media("galerias/Seda/a.jpg", "a", width=640, height=480),
            media("galerias/Seda/b.jpg", "b", width=640, height=480),
        ]

        result = reconcile(source, published, set(), [])

        self.assertEqual(result["assets"][0]["classification"], "conflito")
        self.assertEqual(len(result["assets"][0]["candidate_matches"]), 2)

    def test_source_assets_are_sorted_by_filename_order(self):
        source = [
            media("img/Seda/SEDA/10.jpg", "ten", order=10),
            media("img/Seda/SEDA/02.jpg", "two", order=2),
        ]

        result = reconcile(source, [], set(), [])

        self.assertEqual([item["order"] for item in result["assets"]], [2, 10])


if __name__ == "__main__":
    unittest.main()
