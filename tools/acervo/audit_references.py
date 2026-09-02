#!/usr/bin/env python3
"""Audit active HTML/CSS references during the media-tree migration."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlsplit


ATTRIBUTE_REFERENCE = re.compile(r"(?:src|href)=[\"']([^\"']+)[\"']", re.IGNORECASE)
MEDIA_CONTENT_REFERENCE = re.compile(
    r"content=[\"']((?:\.\./)?(?:img/images|images)/[^\"']+)[\"']", re.IGNORECASE
)
CSS_REFERENCE = re.compile(r"url\(\s*[\"']?([^\"')]+)", re.IGNORECASE)
IGNORED_SCHEMES = {"data", "http", "https", "mailto", "tel", "javascript"}


@dataclass
class AuditReport:
    legacy_references: list[str] = field(default_factory=list)
    missing_assets: list[str] = field(default_factory=list)


def _references(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    matches = ATTRIBUTE_REFERENCE.findall(text)
    if path.suffix.lower() in {".html", ".htm"}:
        matches.extend(MEDIA_CONTENT_REFERENCE.findall(text))
    if path.suffix.lower() == ".css":
        matches.extend(CSS_REFERENCE.findall(text))
    return matches


def _local_path(raw_reference: str) -> str | None:
    reference = unescape(raw_reference.strip())
    if (
        not reference
        or reference.startswith("#")
        or reference.startswith("//")
        or "${" in reference
    ):
        return None
    parsed = urlsplit(reference)
    if parsed.scheme.lower() in IGNORED_SCHEMES:
        return None
    return unquote(parsed.path) or None


def _audit_paths(paths: list[Path]) -> list[Path]:
    supported_suffixes = {".css", ".htm", ".html", ".js"}
    expanded: list[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(
                candidate
                for candidate in sorted(path.rglob("*"))
                if candidate.is_file() and candidate.suffix.lower() in supported_suffixes
            )
        else:
            expanded.append(path)
    return expanded


def audit_files(root: Path, paths: list[Path]) -> AuditReport:
    root = root.resolve()
    report = AuditReport()
    for path in _audit_paths(paths):
        path = path.resolve()
        display_path = path.relative_to(root).as_posix()
        for raw_reference in _references(path):
            local = _local_path(raw_reference)
            if local is None:
                continue
            normalized = local.lstrip("/")
            if normalized.startswith("images/") or normalized.startswith("../images/"):
                report.legacy_references.append(f"{display_path}: {raw_reference}")
            target = root / normalized if local.startswith("/") else path.parent / local
            if not target.resolve().exists():
                report.missing_assets.append(f"{display_path}: {raw_reference}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    report = audit_files(args.root, args.paths)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    raise SystemExit(1 if report.legacy_references or report.missing_assets else 0)


if __name__ == "__main__":
    main()
