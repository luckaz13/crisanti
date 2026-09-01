#!/usr/bin/env python3
"""Render reviewed archive galleries into the bilingual static pages."""

from __future__ import annotations

import argparse
import copy
import html
import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, NavigableString

if __package__:
    from .curate import localize_caption
    from .localize_manifest_pt import localize_manifest_pt
else:
    from curate import localize_caption
    from localize_manifest_pt import localize_manifest_pt


GALLERY_TARGETS = {
    "Seda/SEDA": "seda",
    "Seda/SEDA 2024": "seda-2024",
    "Seda/SEDA BAHIA": "seda-bahia",
    "Peces": "peixes",
    "Ensayos/Collagem": "ensayos-collagem",
    "Ensayos/Emulsión": "ensayos-crema",
    "Ensayos/El Teléfono": "ensayos-el-telefono",
    "Ensayos/La Cocina": "ensayos-la-cocina",
    "Ensayos/Perspectiva": "ensayos-perspectiva",
    "Ensayos/Siluetas": "ensayos-siluetas",
    "Ensayos/Urubús": "ensayos-urubus",
    "Cuadernos": "cadernos",
    "La Escultura/Addis Abbaba": "la-escultura-addis-abbaba",
    "La Escultura/Invierno II": "la-escultura-invierno",
    "La Escultura/Pez III": "la-escultura-pez-iii",
    "La Escultura/Pez IV": "la-escultura-pez-iv",
    "La Escultura/Soies Sauvages": "la-escultura-soies-sauvages",
    "La Fotografía/Cotidiano": "la-fotografia-cotidiano",
    "La Fotografía/Exilio": "la-fotografia-exilio",
    "La Fotografía/Luz Líquida": "la-fotografia-luz-liquida",
    "La Moda": "la-moda",
    "Los Laberintos/Cadaver Exquisito": "los-laberintos-cadaver-exquisito",
    "Los Laberintos/El Calendario": "los-laberintos-el-calendario",
    "Los Laberintos/El Puzzle": "los-laberintos-el-puzzle",
    "Los Laberintos/Las Etiquetas": "los-laberintos-las-etiquetas",
    "Los Laberintos/Memory": "los-laberintos-memory",
    "Los Niños/Cósimo": "los-ninos-cosimo",
    "Los Niños/Der Elefant": "los-ninos-der-elefant",
    "Los Niños/El Ciervo": "los-ninos-el-ciervo",
    "Los Niños/Seis Animales": "los-ninos-seis-animales",
    "Proyectos Especiales/La Fuente y los Simios/Exposición Virtual (La Fuente...)": "proyectos-especiales-la-fuente-y-los-simios",
    "Proyectos Especiales/Master Taxi": "proyectos-especiales-master-taxi",
    "Proyectos Especiales/Vlak": "proyectos-especiales-vlak",
    "Literatura/Ficción/El Nombre": "ficcao-el-nombre",
}

EDITORIAL_FILENAMES = (
    "editorial-seda-ensaios.json",
    "editorial-escultura-fotografia-moda.json",
    "editorial-laberintos-ninos.json",
    "editorial-proyectos-literatura.json",
)

SECTION_LEAD_TARGETS = {
    "Ensayos": "ensayos",
    "La Escultura": "la-escultura",
    "Los Laberintos": "los-laberintos",
    "Literatura/Crítica": "critica",
}


def published_path(source_path: str) -> str:
    relative = Path(source_path).relative_to("img").as_posix()
    return f"img/images/{relative}"


def render_slides(
    assets: list[dict[str, Any]], language: str, *, visible_captions: bool
) -> str:
    slides = []
    for index, asset in enumerate(assets):
        alt = html.escape(asset.get("alt", {}).get(language) or asset["filename"], quote=True)
        source_path = published_path(asset["path"])
        if language == "es":
            source_path = f"../{source_path}"
        source = html.escape(source_path, quote=True)
        caption = asset.get("caption", {}).get(language)
        caption_html = ""
        if visible_captions and caption:
            title = html.escape(caption.get("title") or "")
            meta = " · ".join(
                html.escape(value)
                for value in (caption.get("year"), caption.get("details"))
                if value
            )
            caption_html = '<figcaption class="gallery-caption">'
            if title:
                caption_html += f'<h3 class="gallery-title">{title}</h3>'
            if meta:
                caption_html += f'<p class="gallery-meta">{meta}</p>'
            caption_html += "</figcaption>"
        slides.append(
            f'<div class="gallery-slide" data-index="{index}">'
            '<figure class="gallery-figure">'
            f'<img src="{source}" alt="{alt}" class="gallery-img" loading="lazy" />'
            f"{caption_html}</figure></div>"
        )
    return "\n".join(slides)


def render_series_copy(target: str, content: dict[str, Any], language: str) -> str:
    paragraphs = content.get(language, [])
    rendered = [f"<p>{html.escape(paragraph).replace(chr(10), '<br/>')}</p>" for paragraph in paragraphs]
    for section in content.get("sections", []):
        title = html.escape(section.get("title", {}).get(language, ""))
        rendered.append(f"<h4>{title}</h4>")
        rendered.extend(
            f"<p>{html.escape(paragraph).replace(chr(10), '<br/>')}</p>"
            for paragraph in section.get(language, [])
        )
    if len(rendered) > 2:
        summary = "Leer texto completo" if language == "es" else "Ler texto completo"
        body = rendered[0] + f'<details class="series-copy-more"><summary>{summary}</summary>{"".join(rendered[1:])}</details>'
    else:
        body = "".join(rendered)
    if content.get("credit"):
        body += f'<p class="series-copy-credit">{html.escape(content["credit"])}</p>'
    return f'<template data-series-copy="{html.escape(target, quote=True)}">{body}</template>'


def replace_images_after_leading_media(
    panel: Any, assets: list[dict[str, Any]], language: str
) -> None:
    """Replace image slides while preserving a standalone leading video slide."""
    track = panel.select_one(".gallery-track")
    if track is None:
        raise ValueError(f"gallery track not found: {panel.get('id')}")
    leading = next(
        (slide for slide in track.select(":scope > .gallery-slide") if slide.select_one(".gallery-video")),
        None,
    )
    if leading is None:
        raise ValueError(f"leading video slide not found: {panel.get('id')}")
    leading.extract()
    track.clear()
    track.append(leading)
    slides = BeautifulSoup(
        render_slides(assets, language, visible_captions=True),
        "html.parser",
    )
    track.extend(list(slides.contents))


def render_master_taxi_synopsis(panel: Any, content: dict[str, Any], language: str) -> None:
    """Render the synopsis inline and remove only its legacy document card."""
    for old_synopsis in panel.select(".master-taxi-synopsis"):
        old_synopsis.decompose()
    for document in panel.select(".project-document"):
        name = document.select_one(".project-document__name")
        if name and "sinopsis" in name.get_text(" ", strip=True).casefold().replace("ó", "o"):
            whitespace = document.previous_sibling
            document.decompose()
            if isinstance(whitespace, NavigableString) and not whitespace.strip():
                whitespace.extract()

    title = html.escape(content.get("title", {}).get(language, ""))
    rendered = [f'<section class="master-taxi-synopsis"><h3>{title}</h3>']
    for section in content.get("sections", []):
        heading = html.escape(section.get("title", {}).get(language, ""))
        if heading:
            rendered.append(f"<h4>{heading}</h4>")
        rendered.extend(f"<p>{html.escape(paragraph)}</p>" for paragraph in section.get(language, []))
    rendered.append("</section>")
    synopsis = BeautifulSoup("".join(rendered), "html.parser").section
    viewport = panel.select_one(".gallery-viewport")
    if viewport is None:
        raise ValueError("Master Taxi gallery viewport not found")
    viewport.insert_after(synopsis)


def reorder_el_nombre(fiction: Any, content: dict[str, Any], language: str) -> None:
    """Place El Nombre's rendered copy after its gallery without touching Flores."""
    panel = fiction.find(id="gallery-carousel-ficcao-el-nombre")
    if panel is None:
        raise ValueError("El Nombre gallery not found")
    for old_copy in fiction.select('[data-rendered-series-copy="ficcao-el-nombre"]'):
        old_copy.decompose()
    template = BeautifulSoup(
        render_series_copy("ficcao-el-nombre", content, language),
        "html.parser",
    ).template
    wrapper_soup = BeautifulSoup(
        '<div class="series-copy-display series-copy-display--static" '
        'data-rendered-series-copy="ficcao-el-nombre"></div>',
        "html.parser",
    )
    wrapper = wrapper_soup.div
    wrapper.extend(list(template.contents))

    overview = fiction.select_one(".literatura-fiction-overview")
    if overview is not None:
        panel.insert_after(overview)
        overview.insert_after(wrapper)
    else:
        panel.insert_after(wrapper)


def update_carousel(
    page: str,
    carousel_id: str,
    assets: list[dict[str, Any]],
    language: str,
    visible_captions: bool,
) -> str:
    soup = BeautifulSoup(page, "html.parser")
    carousel = soup.find(id=carousel_id)
    if carousel is None:
        raise ValueError(f"carousel not found: {carousel_id}")
    track = carousel.select_one(".gallery-track")
    if track is None:
        raise ValueError(f"gallery track not found: {carousel_id}")
    track.clear()
    fragment = BeautifulSoup(
        render_slides(assets, language, visible_captions=visible_captions),
        "html.parser",
    )
    track.extend(list(fragment.contents))
    return str(soup)


def clone_tabbed_gallery(
    page: str,
    section_id: str,
    base_target: str,
    new_target: str,
    label: str,
    assets: list[dict[str, Any]],
    language: str,
) -> str:
    soup = BeautifulSoup(page, "html.parser")
    section = soup.find(id=section_id)
    if section is None:
        raise ValueError(f"section not found: {section_id}")
    base_tab = section.select_one(f'.gallery-tab[data-target="{base_target}"]')
    base = section.find(id=f"gallery-carousel-{base_target}")
    if base_tab is None or base is None:
        raise ValueError(f"base gallery not found: {base_target}")
    tab = copy.copy(base_tab)
    tab["data-target"] = new_target
    tab["aria-selected"] = "false"
    tab["class"] = [name for name in tab.get("class", []) if name != "active"]
    tab.string = label
    base_tab.insert_after(tab)
    panel = copy.copy(base)
    panel["id"] = f"gallery-carousel-{new_target}"
    panel["hidden"] = ""
    for tagged in panel.select("[id]"):
        if tagged is not panel:
            del tagged["id"]
    track = panel.select_one(".gallery-track")
    if track is None:
        raise ValueError(f"gallery track not found: {base_target}")
    track.clear()
    fragment = BeautifulSoup(render_slides(assets, language, visible_captions=True), "html.parser")
    track.extend(list(fragment.contents))
    base.insert_after(panel)
    return str(soup)


def _key(asset: dict[str, Any]) -> str:
    return "/".join(part for part in (asset["section"], asset["series"]) if part)


def load_series_editorial(manifest: dict[str, Any], editorial_dir: Path) -> dict[str, Any]:
    """Merge the reviewed editorial sources into a regenerated manifest in memory."""
    result = copy.deepcopy(manifest)
    content = dict(result.get("series_content", {}))
    for filename in EDITORIAL_FILENAMES:
        payload = json.loads((editorial_dir / filename).read_text(encoding="utf-8"))
        content.update(payload.get("series", {}))
    result["series_content"] = content
    return result


def _asset_with_editorial_caption(
    asset: dict[str, Any], series_content: dict[str, Any]
) -> dict[str, Any]:
    override = series_content.get(_key(asset), {}).get("captions", {}).get(asset["filename"])
    captions = asset.get("caption", {})
    source = captions.get("source")
    needs_localization = source and any(
        not isinstance(captions.get(language), dict) for language in ("es", "pt")
    )
    if not override and not needs_localization:
        return asset
    result = copy.deepcopy(asset)
    if needs_localization:
        es_caption, pt_caption = localize_caption(source)
        result.setdefault("caption", {})["es"] = es_caption
        result["caption"]["pt"] = pt_caption
        result = localize_manifest_pt({"assets": [result]})["assets"][0]
    if override:
        result.setdefault("caption", {}).update(copy.deepcopy(override))
    for language in ("es", "pt"):
        caption = result.get("caption", {}).get(language)
        if not isinstance(caption, dict):
            continue
        values = [caption.get(field) for field in ("title", "year", "details")]
        values = [value for value in values if value]
        if values:
            result.setdefault("alt", {})[language] = " — ".join([*values, "Fabio Crisanti"])
    return result


def _apply_section_leads(soup: BeautifulSoup, series_content: dict[str, Any], language: str) -> None:
    for key, section_id in SECTION_LEAD_TARGETS.items():
        value = series_content.get(key, {}).get("lead", {}).get(language)
        if not value:
            continue
        section = soup.find(id=section_id)
        lead = section.select_one(".series-lead, .literatura-intro") if section else None
        if lead is None:
            raise ValueError(f"section lead not found: {section_id}")
        lead.string = value


def _replace_track(panel: Any, assets: list[dict[str, Any]], language: str, captions: bool) -> None:
    track = panel.select_one(".gallery-track")
    if track is None:
        raise ValueError(f"gallery track not found: {panel.get('id')}")
    track.clear()
    fragment = BeautifulSoup(render_slides(assets, language, visible_captions=captions), "html.parser")
    track.extend(list(fragment.contents))


def apply_pt_editorial(page: str, editorial: dict[str, Any]) -> str:
    """Apply reviewed Portuguese prose to legacy criticism cards."""
    soup = BeautifulSoup(page, "html.parser")
    criticism = soup.find(id="critica")
    if criticism is None:
        raise ValueError("criticism section not found: critica")
    intro = criticism.select_one(".literatura-intro")
    if intro is None:
        raise ValueError("criticism introduction not found")
    intro.string = editorial["intro"]
    for article_id, content in editorial.get("articles", {}).items():
        article = criticism.find(id=article_id)
        if article is None:
            raise ValueError(f"criticism article not found: {article_id}")
        excerpt = article.select_one(".literatura-excerpt")
        body = article.select_one(".literatura-full")
        if excerpt is None or body is None:
            raise ValueError(f"criticism article is incomplete: {article_id}")
        excerpt.string = content["excerpt"]
        body.clear()
        for paragraph in content["paragraphs"]:
            tag = soup.new_tag("p")
            tag.string = paragraph
            body.append(tag)
    return str(soup)


def render_page(
    page: str,
    manifest: dict[str, Any],
    language: str,
    pt_editorial: dict[str, Any] | None = None,
) -> str:
    soup = BeautifulSoup(page, "html.parser")
    series_content = manifest.get("series_content", {})
    grouped: dict[str, list[dict[str, Any]]] = {}
    for asset in manifest["assets"]:
        rendered_asset = _asset_with_editorial_caption(asset, series_content)
        grouped.setdefault(_key(rendered_asset), []).append(rendered_asset)
    targets = dict(GALLERY_TARGETS)
    if language == "es":
        targets["Peces"] = "peces"
        targets["Cuadernos"] = "cuadernos"
    for key, target in targets.items():
        panel = soup.find(id=f"gallery-carousel-{target}")
        if panel is None:
            raise ValueError(f"carousel not found: {target}")
        _replace_track(panel, grouped[key], language, captions=key != "Peces")

    standalone_vlak = soup.find(id="gallery-carousel-juego-del-tren")
    if standalone_vlak is None:
        raise ValueError("carousel not found: juego-del-tren")
    replace_images_after_leading_media(
        standalone_vlak,
        grouped["Proyectos Especiales/Vlak"],
        language,
    )

    additions = [
        ("ensayos", "ensayos-el-telefono", "ensayos-gatos", "Gatos", "Ensayos/Gatos"),
        ("los-laberintos", "los-laberintos-el-puzzle", "los-laberintos-la-papa", "La Papa", "Los Laberintos/La Papa"),
        ("la-escultura", "la-escultura-invierno", "la-escultura-invierno-iii", "Invierno III", "La Escultura/Invierno III"),
    ]
    for section_id, base_target, target, label, key in additions:
        section = soup.find(id=section_id)
        existing = section.find(id=f"gallery-carousel-{target}")
        if existing is not None:
            _replace_track(existing, grouped[key], language, captions=True)
            continue
        base_tab = section.select_one(f'.gallery-tab[data-target="{base_target}"]')
        base = section.find(id=f"gallery-carousel-{base_target}")
        if target == "la-escultura-invierno-iii":
            base_tab.string = "Invierno II"
        tab = copy.copy(base_tab)
        tab["data-target"] = target
        tab["aria-selected"] = "false"
        tab["class"] = [name for name in tab.get("class", []) if name != "active"]
        tab.string = label
        base_tab.insert_after(tab)
        panel = copy.copy(base)
        panel["id"] = f"gallery-carousel-{target}"
        panel["hidden"] = ""
        for tagged in panel.select("[id]"):
            if tagged is not panel:
                del tagged["id"]
        _replace_track(panel, grouped[key], language, captions=True)
        base.insert_after(panel)

    fiction = soup.find(id="ficcao")
    fiction_base = fiction.find(id="gallery-carousel-ficcao-el-nombre")
    fiction_tabs = fiction.select_one('.gallery-tabs')
    if fiction_tabs is None:
        fiction_tabs = soup.new_tag("div", attrs={"class": "gallery-tabs", "role": "tablist", "aria-label": "Obras de ficción" if language == "es" else "Obras de ficção"})
        for active, target, label in [(True, "ficcao-el-nombre", "El Nombre"), (False, "ficcao-flores", "Flores")]:
            button = soup.new_tag("button", attrs={"class": "gallery-tab active" if active else "gallery-tab", "role": "tab", "aria-selected": "true" if active else "false", "data-target": target})
            button.string = label
            fiction_tabs.append(button)
        fiction_base.insert_before(fiction_tabs)
    flores = fiction.find(id="gallery-carousel-ficcao-flores")
    if flores is None:
        flores = copy.copy(fiction_base)
        flores["id"] = "gallery-carousel-ficcao-flores"
        flores["hidden"] = ""
        for tagged in flores.select("[id]"):
            if tagged is not flores:
                del tagged["id"]
        fiction_base.insert_after(flores)
    _replace_track(flores, grouped["Literatura/Ficción/Flores"], language, captions=True)

    for old_template in soup.select('template[data-series-copy]'):
        old_template.decompose()
    old_overview = fiction.select_one('.literatura-fiction-overview')
    if old_overview:
        old_overview.decompose()

    content_targets = {
        "Seda/SEDA": ("series", "seda"),
        "Seda/SEDA BAHIA": ("seda-bahia", "seda-bahia"),
        "Ensayos/El Teléfono": ("ensayos", "ensayos-el-telefono"),
        "Ensayos/Emulsión": ("ensayos", "ensayos-crema"),
        "Ensayos/Urubús": ("ensayos", "ensayos-urubus"),
        "La Fotografía/Cotidiano": ("la-fotografia", "la-fotografia-cotidiano"),
        "La Fotografía/Luz Líquida": ("la-fotografia", "la-fotografia-luz-liquida"),
        "La Moda": ("la-moda", "la-moda"),
        "Los Laberintos/Cadaver Exquisito": ("los-laberintos", "los-laberintos-cadaver-exquisito"),
        "Los Laberintos/El Calendario": ("los-laberintos", "los-laberintos-el-calendario"),
        "Los Laberintos/El Puzzle": ("los-laberintos", "los-laberintos-el-puzzle"),
        "Los Laberintos/La Papa": ("los-laberintos", "los-laberintos-la-papa"),
        "Los Niños/Cósimo": ("los-ninos", "los-ninos-cosimo"),
        "Los Niños/Der Elefant": ("los-ninos", "los-ninos-der-elefant"),
        "Los Niños/El Ciervo": ("los-ninos", "los-ninos-el-ciervo"),
        "Los Niños/Seis Animales": ("los-ninos", "los-ninos-seis-animales"),
        "Proyectos Especiales/La Fuente y los Simios": ("proyectos-especiales", "proyectos-especiales-la-fuente-y-los-simios"),
        "Proyectos Especiales/Vlak": ("proyectos-especiales", "proyectos-especiales-vlak"),
        "Literatura/Ficción/El Nombre": ("ficcao", "ficcao-el-nombre"),
        "Literatura/Ficción/Flores": ("ficcao", "ficcao-flores"),
    }
    for key, (section_id, target) in content_targets.items():
        content = series_content.get(key)
        if not content:
            continue
        section = soup.find(id=section_id)
        fragment = BeautifulSoup(render_series_copy(target, content, language), "html.parser")
        section.append(fragment.template)
    fiction_overview = series_content.get("Literatura/Ficción")
    if fiction_overview:
        fragment = BeautifulSoup(render_series_copy("ficcao-overview", fiction_overview, language), "html.parser")
        overview = soup.new_tag("div", attrs={"class": "literatura-fiction-overview"})
        overview.extend(list(fragment.template.contents))
        fiction_tabs.insert_before(overview)
    el_nombre_content = series_content.get("Literatura/Ficción/El Nombre")
    if el_nombre_content:
        reorder_el_nombre(fiction, el_nombre_content, language)

    master_taxi = soup.find(id="gallery-carousel-proyectos-especiales-master-taxi")
    master_taxi_content = series_content.get("Proyectos Especiales/Master Taxi", {}).get("synopsis")
    if master_taxi is not None and master_taxi_content:
        render_master_taxi_synopsis(master_taxi, master_taxi_content, language)

    _apply_section_leads(soup, series_content, language)
    rendered = str(soup)
    if language == "pt" and pt_editorial:
        rendered = apply_pt_editorial(rendered, pt_editorial)
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--pt", type=Path, required=True)
    parser.add_argument("--es", type=Path, required=True)
    parser.add_argument(
        "--pt-editorial",
        type=Path,
        default=Path("data/acervo/editorial-literatura-critica.json"),
    )
    args = parser.parse_args()
    manifest = load_series_editorial(
        json.loads(args.manifest.read_text(encoding="utf-8")),
        args.manifest.parent,
    )
    pt_editorial = json.loads(args.pt_editorial.read_text(encoding="utf-8"))
    args.pt.write_text(
        render_page(args.pt.read_text(encoding="utf-8"), manifest, "pt", pt_editorial),
        encoding="utf-8",
    )
    args.es.write_text(render_page(args.es.read_text(encoding="utf-8"), manifest, "es"), encoding="utf-8")


if __name__ == "__main__":
    main()
