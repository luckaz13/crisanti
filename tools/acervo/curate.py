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


def apply_artist_pdf_revisions(
    manifest: dict[str, Any], documents: list[dict[str, Any]]
) -> dict[str, Any]:
    """Apply the approved publication curation for the revised artist PDFs."""
    result = apply_fichas(manifest, documents) if documents else deepcopy(manifest)
    curated_assets = []
    for asset in result.get("assets", []):
        key = "/".join(part for part in (asset.get("section"), asset.get("series")) if part)
        if key == "La Escultura/Verde":
            continue
        if asset.get("section") == "Los Niños":
            source = asset.get("caption", {}).get("source")
            if source and source.get("details"):
                value = source["details"]
                value = re.sub(r"(?<=\d{4})(?=[A-ZÁÉÍÓÚ])", ". ", value)
                value = re.sub(
                    r"(?i)Materiais?:(?=\S)",
                    lambda match: f"{match.group(0)} ",
                    value,
                )
                value = re.sub(
                    r"(?i)Materiales:(?=\S)",
                    lambda match: f"{match.group(0)} ",
                    value,
                )
                value = re.sub(
                    r"(?<=[a-záéíóú])(?=(?:Algodão|Acrílico|Cerâmica|Colagem|Impressão|Papel|Tecido))",
                    ". ",
                    value,
                )
                source["details"] = _readable_details(value) or None
        curated_assets.append(asset)
    result["assets"] = curated_assets
    return result


def _replace_all(value: str | None, replacements: list[tuple[str, str]]) -> str | None:
    if value is None:
        return None
    for old, new in replacements:
        value = value.replace(old, new)
    return value


def localize_pt_text(value: str | None) -> str | None:
    """Localize recurring documentary labels without translating proper titles."""
    if value is None:
        return None
    replacements = [
        ("Vista general de la seria", "Vista geral da série"),
        ("Vista general de la serie", "Vista geral da série"),
        ("Vista general serie", "Vista geral da série"),
        ("Retiro de tapa", "Verso da capa"),
        ("retiro de contratapa", "verso da contracapa"),
        ("retiro de cpntratapa", "verso da contracapa"),
        ("Imágenes del", "Imagens do"),
        ("Ilustraciones de las fichas", "Ilustrações das fichas"),
        ("Copias fotográficas tomadas de la serie", "Cópias fotográficas feitas a partir da série"),
        ("tomadas de la serie", "feitas a partir da série"),
        ("desde la serie", "da série"),
        ("Detalle del personaje", "Detalhe da personagem"),
        ("Detalle de rabiola", "Detalhe da rabiola"),
        ("Detalle de vela", "Detalhe da vela"),
        ("Detalle rabiola", "Detalhe da rabiola"),
        ("Detalle", "Detalhe"),
        ("detalle", "detalhe"),
        ("Bocetos", "Esboços"),
        ("Boceto", "Esboço"),
        ("boceto", "esboço"),
        ("Materiales:", "Materiais:"),
        ("Emulsión fotográfica", "Emulsão fotográfica"),
        ("sobre lienzo imprimado", "sobre tela preparada"),
        ("Proceso de construcción", "Processo de construção"),
        ("proceso de construcción", "processo de construção"),
        ("Gráficos descriptivos", "Gráficos descritivos"),
        ("Elementos del universo del cuento", "Elementos do universo do conto"),
        ("Esquema narrativo (esboço)", "Esquema narrativo (esboço)"),
        ("Tapas de", "Capas de"),
        ("Ejemplares de", "Exemplares de"),
        ("Encuadernación", "Encadernação"),
        ("Contratapa de", "Contracapa de"),
        ("Diseño digital", "Design digital"),
        ("Estructuras de Bambú", "Estruturas de bambu"),
        ("Páginas centrales", "Páginas centrais"),
        ("Cadaver exquisito", "Cadáver exquisito"),
        ("Plano Contrapicado Iglesia de Garopaba", "Plano em contra-plongée da Igreja de Garopaba"),
        ("Galería del Consulado Argentino de la República Argentina en Colonia del Sacramento, Uruguay", "Galeria do Consulado da República Argentina em Colônia do Sacramento, Uruguai"),
        ("La Salada, Pcia. De Bs. As. - Argentina.", "La Salada, Província de Buenos Aires, Argentina."),
        ("Esque líneas narrativas", "Esquema de linhas narrativas"),
        ("Seda salvaje", "Seda selvagem"),
        ("SEDA SALVAJE", "SEDA SELVAGEM"),
        ("Hilos Encerados", "Fios encerados"),
        ("Lana Natural", "Lã natural"),
        ("Gomaespuma", "Espuma"),
        ("Cartapesta", "Papel machê"),
        ("Papeles Metalizados", "Papéis metalizados"),
        ("Lienzo Crudo", "Tela crua"),
        ("Hilos de", "Fios de"),
        ("Corcho", "Cortiça"),
        ("Oro", "Ouro"),
        ("Perla", "Pérola"),
        ("Poliester", "Poliéster"),
        ("Madera", "Madeira"),
        ("Cartón", "Papelão"),
        ("Acero", "Aço"),
        ("Alambre", "Arame"),
        ("Piel", "Pele"),
        ("Cuero", "Couro"),
        ("Terciopelo", "Veludo"),
        ("Lana", "Lã"),
        ("Algodón", "Algodão"),
        ("Cerámica", "Cerâmica"),
        ("Impresión digital", "Impressão digital"),
        ("Collage", "Colagem"),
        ("collage", "colagem"),
        (" y colagem", " e colagem"),
        (" y cromía", " e cromia"),
        (" y síntesis", " e síntese"),
        (" y página", " e página"),
        (" y verso", " e verso"),
        ("Galería", "Galeria"),
        ("Chaleco", "Colete"),
        ("Lino", "Linho"),
        ("Raso", "Cetim"),
        ("Caja", "Caixa"),
        ("caja", "caixa"),
        ("Cuarto", "Quarto"),
        ('La Cuadratura del Círculo en la Perspectiva "Ojo de Pez"', 'A Quadratura do Círculo na Perspectiva "Olho de Peixe"'),
    ]
    value = _replace_all(value, replacements) or ""
    value = re.sub(r"\bPáginas?(\s+\d+)\s+y\s+(?=\d)", lambda match: match.group(0).replace(" y ", " e "), value)
    value = re.sub(r'(["”])\s+y\s+(["“])', r'\1 e \2', value)
    value = value.replace("ContratapaAcrílicos", "Contracapa. Acrílicos")
    value = value.replace("TapaAcrílicos", "Capa. Acrílicos")
    value = value.replace("tapa de caixa", "capa da caixa")
    value = value.replace("tapa de", "capa de")
    value = value.replace("Contratapa", "Contracapa")
    value = value.replace("Tapa", "Capa")
    value = value.replace("Capa del", "Capa do")
    value = re.sub(r"(?<=\d)Acrílicos", ". Acrílicos", value)
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
    pt_title = localize_pt_text(_replace_all(
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
    ))
    pt_details = localize_pt_text(_replace_all(
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
    ))
    return (
        {"title": es_title, "year": source.get("year"), "details": es_details},
        {"title": pt_title, "year": source.get("year"), "details": pt_details},
    )
