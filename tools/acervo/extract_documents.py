#!/usr/bin/env python3
"""Extract structured text from the editorial archive documents."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile


def _text(element: ElementTree.Element) -> str:
    return "".join(
        node.text or "" for node in element.iter() if node.tag.endswith("}t")
    ).strip()


def _numbered_xml_key(name: str) -> tuple[str, int]:
    match = re.search(r"(\d+)\.xml$", name)
    return (name[: match.start()] if match else name, int(match.group(1)) if match else -1)


@dataclass(frozen=True)
class DocumentText:
    path: str
    kind: str
    status: str
    paragraphs: list[str] = field(default_factory=list)
    tables: list[list[list[str]]] = field(default_factory=list)
    slides: list[list[str]] = field(default_factory=list)
    error: str | None = None


def extract_docx(path: Path) -> DocumentText:
    try:
        with ZipFile(path) as archive:
            root = ElementTree.fromstring(archive.read("word/document.xml"))
        paragraphs = [text for node in root.iter() if node.tag.endswith("}p") if (text := _text(node))]
        tables: list[list[list[str]]] = []
        for table in (node for node in root.iter() if node.tag.endswith("}tbl")):
            rows: list[list[str]] = []
            for row in (node for node in table if node.tag.endswith("}tr")):
                rows.append([_text(cell) for cell in row if cell.tag.endswith("}tc")])
            tables.append(rows)
        return DocumentText(str(path), "docx", "ok", paragraphs=paragraphs, tables=tables)
    except (BadZipFile, KeyError, ElementTree.ParseError, OSError) as error:
        return DocumentText(str(path), "docx", "error", error=str(error))


def extract_pptx(path: Path) -> DocumentText:
    try:
        with ZipFile(path) as archive:
            names = sorted(
                (
                    name
                    for name in archive.namelist()
                    if name.startswith("ppt/slides/slide") and name.endswith(".xml")
                ),
                key=_numbered_xml_key,
            )
            slides = []
            for name in names:
                root = ElementTree.fromstring(archive.read(name))
                slides.append(
                    [
                        node.text.strip()
                        for node in root.iter()
                        if node.tag.endswith("}t") and node.text and node.text.strip()
                    ]
                )
        return DocumentText(str(path), "pptx", "ok", slides=slides)
    except (BadZipFile, ElementTree.ParseError, OSError) as error:
        return DocumentText(str(path), "pptx", "error", error=str(error))


def extract_pdf(path: Path) -> DocumentText:
    executable = shutil.which("pdftotext")
    if not executable:
        return DocumentText(str(path), "pdf", "unavailable", error="pdftotext not installed")
    try:
        result = subprocess.run(
            [executable, "-layout", str(path), "-"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        paragraphs = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return DocumentText(str(path), "pdf", "ok", paragraphs=paragraphs)
    except (OSError, subprocess.SubprocessError) as error:
        return DocumentText(str(path), "pdf", "error", error=str(error))


def scan_documents(root: Path) -> list[DocumentText]:
    extractors = {".docx": extract_docx, ".pptx": extract_pptx, ".pdf": extract_pdf}
    documents = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().casefold()):
        extractor = extractors.get(path.suffix.casefold())
        if path.is_file() and extractor:
            extracted = extractor(path)
            documents.append(
                DocumentText(
                    path=f"img/{path.relative_to(root).as_posix()}",
                    kind=extracted.kind,
                    status=extracted.status,
                    paragraphs=extracted.paragraphs,
                    tables=extracted.tables,
                    slides=extracted.slides,
                    error=extracted.error,
                )
            )
    return documents


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    documents = scan_documents(args.source)
    payload = {
        "schema_version": 1,
        "source_root": "img",
        "documents": [asdict(document) for document in documents],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
