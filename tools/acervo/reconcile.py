#!/usr/bin/env python3
"""Reconcile authoritative archive records with the currently published site."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable

if __package__:
    from .inventory import natural_key
else:
    from inventory import natural_key


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for attribute in ("src", "href", "poster"):
            value = values.get(attribute)
            if value and not value.startswith(("http://", "https://", "mailto:", "#")):
                self.references.add(value.removeprefix("./").removeprefix("../"))


def extract_references(paths: Iterable[Path]) -> set[str]:
    references: set[str] = set()
    for path in paths:
        parser = ReferenceParser()
        parser.feed(path.read_text(encoding="utf-8"))
        references.update(parser.references)
    return references


def _source_sort_key(record: dict[str, Any]) -> tuple[object, ...]:
    return (
        record.get("section", "").casefold(),
        record.get("series", "").casefold(),
        record.get("order") is None,
        record.get("order") if record.get("order") is not None else -1,
        natural_key(record.get("filename", "")),
    )


def _published_url(path: str) -> str:
    return path if path.startswith("images/") else f"images/{path}"


def reconcile(
    source: list[dict[str, Any]],
    published: list[dict[str, Any]],
    references: set[str],
    documents: list[dict[str, Any]],
) -> dict[str, Any]:
    published_by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    published_by_dimensions: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for record in published:
        published_by_hash[record["sha256"]].append(record)
        published_by_dimensions[(record["width"], record["height"])].append(record)

    source_hashes = {record["sha256"] for record in source}
    assets: list[dict[str, Any]] = []
    for record in sorted(source, key=_source_sort_key):
        exact = published_by_hash.get(record["sha256"], [])
        candidates = published_by_dimensions.get((record["width"], record["height"]), [])
        if exact:
            classification = "atual"
        elif len(candidates) > 1:
            classification = "conflito"
        else:
            classification = "novo"
        assets.append(
            record
            | {
                "classification": classification,
                "published_matches": sorted(_published_url(item["path"]) for item in exact),
                "candidate_matches": sorted(_published_url(item["path"]) for item in candidates) if not exact else [],
                "visual_status": "matched-by-hash" if exact else "pending",
                "caption": {"source": None, "es": None, "pt": None},
                "alt": {"es": None, "pt": None},
            }
        )

    legacy = []
    for record in sorted(published, key=lambda item: natural_key(item["path"])):
        if record["sha256"] in source_hashes:
            continue
        url = _published_url(record["path"])
        legacy.append(
            record
            | {
                "path": url,
                "classification": "legado-em-uso" if url in references else "substituído",
            }
        )

    return {
        "schema_version": 1,
        "assets": assets,
        "legacy": legacy,
        "documents": documents,
    }


def write_report(manifest: dict[str, Any], output: Path) -> None:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for asset in manifest["assets"]:
        grouped[(asset["section"], asset["series"])].append(asset)
    totals = Counter(asset["classification"] for asset in manifest["assets"])
    legacy_totals = Counter(asset["classification"] for asset in manifest["legacy"])
    lines = [
        "# Relatório de reconciliação do acervo",
        "",
        "## Totais",
        "",
        f"- Fonte atual: {len(manifest['assets'])} imagens",
        f"- Atuais por hash: {totals['atual']}",
        f"- Novas sem candidato ambíguo: {totals['novo']}",
        f"- Conflitos para revisão visual: {totals['conflito']}",
        f"- Legado em uso: {legacy_totals['legado-em-uso']}",
        f"- Publicadas sem uso atual: {legacy_totals['substituído']}",
        "",
        "## Galerias",
        "",
    ]
    for (section, series), assets in sorted(grouped.items()):
        counts = Counter(asset["classification"] for asset in assets)
        name = " / ".join(part for part in (section, series) if part)
        lines.extend(
            [
                f"### {name}",
                "",
                f"- Total: {len(assets)}",
                f"- Atuais: {counts['atual']}",
                f"- Novas: {counts['novo']}",
                f"- Conflitos: {counts['conflito']}",
            ]
        )
        pending = [asset["path"] for asset in assets if asset["classification"] != "atual"]
        if pending:
            lines.append(f"- Revisar: {', '.join(pending)}")
        lines.append("")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--documents", type=Path, required=True)
    parser.add_argument("--html", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    documents_payload = json.loads(args.documents.read_text(encoding="utf-8"))
    manifest = reconcile(
        inventory["source"],
        inventory["published"],
        extract_references(args.html),
        documents_payload["documents"],
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(manifest, args.report)


if __name__ == "__main__":
    main()
