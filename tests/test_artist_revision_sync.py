import unittest
from pathlib import Path

from tools.acervo.sync_artist_revisions import build_sync_plan


ROOT = Path(__file__).resolve().parents[1]


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


if __name__ == "__main__":
    unittest.main()
