"""Helpers for turning numbered fichas into structured editorial captions."""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import PurePosixPath
from typing import Any


ENTRY_PATTERN = re.compile(r"(?<!\d)(\d{2})(?=\s*[“\"A-ZÁÉÍÓÚ])")


def split_numbered_entries(text: str) -> dict[str, str]:
    text = re.sub(r"(20\d{2})(\d{2})(?=\s*[“\"])", r"\1 \2", text)
    matches = list(ENTRY_PATTERN.finditer(text))
    entries: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        entries[match.group(1)] = text[match.end() : end].strip()
    return entries


def _readable_details(text: str) -> str:
    text = re.sub(r"(?<=\.)(?=[A-ZÁÉÍÓÚ])", " ", text)
    text = re.sub(
        r"(?<=[a-záéíóú])(?=(?:Acrílico|Bambú|Collage|Carimbo|Algodón|Papel|Tinta|Dorado|Tecido))",
        ". ",
        text,
    )
    return " ".join(text.split()).strip()


def parse_caption(raw: str) -> dict[str, str | None]:
    value = raw.strip()
    title = None
    quoted = re.match(r"[“\"]([^”\"]+)[”\"]", value)
    if quoted:
        title = quoted.group(1).strip()
        value = value[quoted.end() :]
    else:
        year_position = re.search(r"20\d{2}", value)
        if year_position:
            title = value[: year_position.start()].strip() or None
            value = value[year_position.start() :]
        elif value:
            title = value
            value = ""
    year_match = re.match(r"(20\d{2})", value)
    year = year_match.group(1) if year_match else None
    if year_match:
        value = value[year_match.end() :]
    return {"title": title, "year": year, "details": _readable_details(value) or None}


def apply_fichas(
    manifest: dict[str, Any], documents: list[dict[str, Any]]
) -> dict[str, Any]:
    result = deepcopy(manifest)
    fichas: dict[str, dict[str, str]] = {}
    for document in documents:
        path = PurePosixPath(document["path"])
        if "ficha" not in path.name.casefold() or path.suffix.casefold() != ".docx":
            continue
        entries = split_numbered_entries(" ".join(document.get("paragraphs", [])))
        if entries:
            fichas[path.parent.as_posix()] = entries
    for asset in result.get("assets", []):
        path = PurePosixPath(asset["path"])
        number = re.match(r"^(\d+)", asset["filename"])
        raw = fichas.get(path.parent.as_posix(), {}).get(number.group(1) if number else "")
        if raw:
            asset["caption"]["source"] = parse_caption(raw)
    return result


def _replace_all(value: str | None, replacements: list[tuple[str, str]]) -> str | None:
    if value is None:
        return None
    for old, new in replacements:
        value = value.replace(old, new)
    return value


def localize_caption(
    source: dict[str, str | None],
) -> tuple[dict[str, str | None], dict[str, str | None]]:
    es_title = _replace_all(
        source.get("title"),
        [("Primitivo Iii", "Primitivo III"), ("IiI", "III")],
    )
    es_details = _replace_all(
        source.get("details"),
        [
            ("Toma directa teléfono", "Toma directa con teléfono"),
            ("Caneta sobra papel", "Bolígrafo sobre papel"),
            ("Caneta sobre papel", "Bolígrafo sobre papel"),
            ("Papel Craft", "Papel kraft"),
            ("Tecido de renda", "Tejido de encaje"),
            ("Carimbo", "Sello"),
            ("Poliester", "Poliéster"),
            ("Preceso de Construcción", "Proceso de construcción"),
            ("Gsropaba", "Garopaba"),
        ],
    )
    pt_title = _replace_all(
        es_title,
        [
            ("Huesos", "Ossos"),
            ("Estudio", "Estudo"),
            ("Ideografía China", "Ideografia Chinesa"),
            ("Emulsión", "Emulsão"),
            ("Pez", "Peixe"),
            ("Ilustración", "Ilustração"),
            ("Bocetos", "Esboços"),
        ],
    )
    pt_details = _replace_all(
        es_details,
        [
            ("Toma directa con teléfono", "Captura direta com telefone"),
            ("tratamiento digital", "tratamento digital"),
            ("intervención digital", "intervenção digital"),
            ("collage digital", "colagem digital"),
            ("Collage", "Colagem"),
            ("Bolígrafo sobre papel", "Caneta sobre papel"),
            ("Acrílico sobre papel de seda", "Acrílico sobre papel de seda"),
            ("Tejido de encaje", "Tecido de renda"),
            ("Tinta China", "Tinta nanquim"),
            ("Dorado a la hoja", "Douração a folha"),
            ("Algodón", "Algodão"),
            ("Bambú", "Bambu"),
            ("Sello", "Carimbo"),
            ("Papel kraft", "Papel kraft"),
            ("Materiales:", "Materiais:"),
            ("Poliéster", "Poliéster"),
            ("Cemento de contacto", "Cola de contato"),
            ("Playa", "Praia"),
            ("Proceso de construcción", "Processo de construção"),
            ("Toma directa", "Captura direta"),
            ("Vidrio", "Vidro"),
            ("Acero", "Aço"),
            ("Fieltro", "Feltro"),
            (" y collage", " e colagem"),
            ("Diseño digital", "Design digital"),
            ("Carbón sobre papel", "Carvão sobre papel"),
        ],
    )
    return (
        {"title": es_title, "year": source.get("year"), "details": es_details},
        {"title": pt_title, "year": source.get("year"), "details": pt_details},
    )
