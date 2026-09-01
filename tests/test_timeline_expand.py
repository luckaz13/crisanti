import re
import json
import subprocess
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


class ExpandableTimelineTests(unittest.TestCase):
    def test_all_timeline_entries_are_available_without_javascript(self):
        for page in ("index.html", "es/index.html"):
            with self.subTest(page=page):
                soup = BeautifulSoup((ROOT / page).read_text(encoding="utf-8"), "html.parser")
                timeline = soup.select_one(".timeline")
                self.assertEqual(2, len(timeline.select(":scope > .timeline-item")))
                collapsible = timeline.select_one(":scope > .timeline-collapsible")
                self.assertIsNotNone(collapsible)
                self.assertFalse(collapsible.has_attr("hidden"))
                self.assertEqual(4, len(collapsible.select(":scope > .timeline-item")))
                button = timeline.select_one("button[data-timeline-toggle]")
                self.assertTrue(button.has_attr("hidden"))
                self.assertFalse(button.has_attr("aria-expanded"))

    def test_toggle_controls_the_collapsible_region_and_uses_native_button_activation(self):
        for page in ("index.html", "es/index.html"):
            with self.subTest(page=page):
                soup = BeautifulSoup((ROOT / page).read_text(encoding="utf-8"), "html.parser")
                button = soup.select_one("button[data-timeline-toggle]")
                collapsible = soup.select_one(".timeline-collapsible")
                self.assertIsNotNone(button)
                self.assertEqual(collapsible.get("id"), button.get("aria-controls"))
                self.assertEqual("button", button.name)

    def test_controller_enhances_fallback_and_measures_only_after_collapse_reflow(self):
        source_path = json.dumps(str(ROOT / "js/main.js"))
        fixture = f"""
const fs = require('fs');
const source = fs.readFileSync({source_path}, 'utf8');
const start = source.indexOf('(function initExpandableTimeline()');
const closer = '\\n' + String.fromCharCode(125) + ')();';
const end = source.indexOf(closer, start) + closer.length;
const controller = source.slice(start, end);
const events = [];
const listeners = {{}};
let top = 24;
const toggle = {{
  hidden: true,
  dataset: {{ labelMore: 'Ver mais', labelLess: 'Ver menos' }},
  textContent: 'Ver mais',
  attributes: {{ 'aria-controls': 'timeline-more-pt' }},
  getAttribute(name) {{ return this.attributes[name] ?? null; }},
  setAttribute(name, value) {{ this.attributes[name] = String(value); }},
  removeAttribute(name) {{ delete this.attributes[name]; }},
  addEventListener(name, handler) {{ listeners[name] = handler; }},
  getBoundingClientRect() {{ events.push(`measure:${{top}}`); return {{ top }}; }},
}};
let collapsibleHidden = false;
const collapsible = {{
  get hidden() {{ return collapsibleHidden; }},
  set hidden(value) {{
    collapsibleHidden = value;
    events.push(`hidden:${{value}}`);
    if (value) top = -18;
  }},
}};
global.$ = selector => selector === '[data-timeline-toggle]' ? toggle : null;
global.document = {{ getElementById: id => id === 'timeline-more-pt' ? collapsible : null }};
global.window = {{
  requestAnimationFrame: callback => {{ events.push('raf'); callback(); }},
  scrollBy: options => events.push(`scroll:${{options.top}}`),
}};
eval(controller);
const afterInit = {{ hidden: collapsible.hidden, toggleHidden: toggle.hidden, expanded: toggle.getAttribute('aria-expanded'), label: toggle.textContent }};
events.length = 0;
listeners.click();
const afterExpand = {{ hidden: collapsible.hidden, expanded: toggle.getAttribute('aria-expanded'), label: toggle.textContent }};
events.length = 0;
listeners.click();
console.log(JSON.stringify({{ afterInit, afterExpand, collapseEvents: events }}));
"""
        result = subprocess.run(
            ["node", "-e", fixture], cwd=ROOT, capture_output=True, text=True
        )
        self.assertEqual(0, result.returncode, result.stderr)
        state = json.loads(result.stdout)
        self.assertEqual(
            {"hidden": True, "toggleHidden": False, "expanded": "false", "label": "Ver mais"},
            state["afterInit"],
        )
        self.assertEqual(
            {"hidden": False, "expanded": "true", "label": "Ver menos"},
            state["afterExpand"],
        )
        self.assertEqual(["hidden:true", "raf", "measure:-18", "scroll:-18"], state["collapseEvents"])

    def test_toggle_stays_aligned_with_the_compact_timeline(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        compact_timeline = css[css.index("RESPONSIVE: GALLERY TABS & TIMELINE") :]
        rule = re.search(r"\.timeline-toggle\s*\{([^}]+)\}", compact_timeline)
        self.assertIsNotNone(rule)
        self.assertIn("margin-left: 1.5rem;", rule.group(1))


if __name__ == "__main__":
    unittest.main()
