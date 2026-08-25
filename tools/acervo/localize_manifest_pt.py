#!/usr/bin/env python3
"""Apply reviewed recurring PT-BR localization rules to manifest captions."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

if __package__:
    from .curate import localize_pt_text
else:
    from curate import localize_pt_text


TITLE_OVERRIDES = {
    "img/Ensayos/Collagem/01.jpg": "Collage I",
    "img/Ensayos/Collagem/02.jpg": "Collage II",
    "img/Ensayos/Collagem/03.jpg": "Collage III",
    "img/Los Niños/Der Elefant/07.jpg": "Páginas 10 e 11",
    "img/Los Niños/Der Elefant/08.jpg": "Páginas 12 e 13",
    "img/Los Niños/Der Elefant/09.jpg": "Páginas 14 e 15",
    "img/Los Niños/Der Elefant/10.jpg": "Páginas 16 e 17",
    "img/Los Niños/Der Elefant/11.jpg": "Páginas 18 e 19",
    "img/Los Niños/Der Elefant/12.jpg": "Páginas 20 e 21",
    "img/Los Niños/Der Elefant/13.jpg": "Páginas 22 e 23",
    "img/Los Niños/Der Elefant/14.jpg": "Páginas 24 e 25",
    "img/Los Niños/Der Elefant/15.jpg": "Páginas 26 e 27",
}


def localize_manifest_pt(manifest: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(manifest)
    for asset in result.get("assets", []):
        caption = asset.get("caption", {}).get("pt")
        if isinstance(caption, dict):
            for field in ("title", "details"):
                caption[field] = localize_pt_text(caption.get(field))
            if asset.get("path") in TITLE_OVERRIDES:
                caption["title"] = TITLE_OVERRIDES[asset["path"]]
        alt = asset.get("alt", {}).get("pt")
        if isinstance(alt, str):
            asset["alt"]["pt"] = localize_pt_text(alt)
        if isinstance(caption, dict):
            parts = [caption.get(field) for field in ("title", "year", "details")]
            parts = [part for part in parts if part]
            if parts:
                asset.setdefault("alt", {})["pt"] = " — ".join([*parts, "Fabio Crisanti"])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    localized = localize_manifest_pt(manifest)
    args.manifest.write_text(
        json.dumps(localized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
