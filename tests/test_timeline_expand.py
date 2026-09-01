import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


class ExpandableTimelineTests(unittest.TestCase):
    def test_only_the_first_third_of_each_timeline_is_visible_without_javascript(self):
        for page in ("index.html", "es/index.html"):
            with self.subTest(page=page):
                soup = BeautifulSoup((ROOT / page).read_text(encoding="utf-8"), "html.parser")
                timeline = soup.select_one(".timeline")
                self.assertEqual(2, len(timeline.select(":scope > .timeline-item")))
                collapsible = timeline.select_one(":scope > .timeline-collapsible[hidden]")
                self.assertIsNotNone(collapsible)
                self.assertEqual(4, len(collapsible.select(":scope > .timeline-item")))

    def test_toggle_controls_the_collapsible_region_and_uses_native_button_activation(self):
        for page in ("index.html", "es/index.html"):
            with self.subTest(page=page):
                soup = BeautifulSoup((ROOT / page).read_text(encoding="utf-8"), "html.parser")
                button = soup.select_one("button[data-timeline-toggle]")
                collapsible = soup.select_one(".timeline-collapsible")
                self.assertIsNotNone(button)
                self.assertEqual(collapsible.get("id"), button.get("aria-controls"))
                self.assertEqual("button", button.name)

    def test_controller_updates_state_labels_and_prevents_focus_scroll_jumps(self):
        script = (ROOT / "js/main.js").read_text(encoding="utf-8")
        self.assertIn("function initExpandableTimeline()", script)
        self.assertIn("toggle.addEventListener('click',", script)
        self.assertIn("collapsible.hidden = !isExpanded;", script)
        self.assertIn("toggle.setAttribute('aria-expanded', String(isExpanded));", script)
        self.assertIn("toggle.textContent = isExpanded ? lessLabel : moreLabel;", script)
        self.assertIn("const toggleTopBeforeCollapse = toggle.getBoundingClientRect().top;", script)
        self.assertIn("if (!isExpanded && toggleTopBeforeCollapse < 0)", script)
        self.assertIn("window.scrollBy({ top: toggle.getBoundingClientRect().top, behavior: 'auto' });", script)

    def test_toggle_stays_aligned_with_the_compact_timeline(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        compact_timeline = css[css.index("RESPONSIVE: GALLERY TABS & TIMELINE") :]
        rule = re.search(r"\.timeline-toggle\s*\{([^}]+)\}", compact_timeline)
        self.assertIsNotNone(rule)
        self.assertIn("margin-left: 1.5rem;", rule.group(1))


if __name__ == "__main__":
    unittest.main()
