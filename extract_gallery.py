#!/usr/bin/env python3
"""
Extrai dados de todos os posts do Instagram e gera o HTML da seção Galeria.
"""

import os
import re
import json
from pathlib import Path

GALERIA_DIR = Path(
    "/home/lucas/Projetos/cristanti/code_sandbox_light_7db1e7f9_1776125489/images/fabio.crisanti.artes.plasticas"
)
OUTPUT_HTML = Path(
    "/home/lucas/Projetos/cristanti/code_sandbox_light_7db1e7f9_1776125489/galeria-items.html"
)


def get_caption(txt_path):
    """Extrai a legenda do arquivo .txt, removendo hashtags."""
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    content_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or stripped == "":
            continue
        content_lines.append(stripped)

    return "\n".join(content_lines) if content_lines else ""


def find_images_for_post(txt_basename):
    """Encontra todas as imagens associadas a um post .txt."""
    prefix = txt_basename.replace(".txt", "")
    images = []
    for ext in [".webp", ".jpg"]:
        img_path = GALERIA_DIR / (prefix + ext)
        if img_path.exists():
            # Caminho relativo ao diretório do projeto (index.html está no parent do images/)
            images.append(f"fabio.crisanti.artes.plasticas/{prefix}{ext}")
    return images


def extract_info(caption):
    """Extrai informações estruturadas da legenda."""
    info = {
        "title": "",
        "year": "",
        "technique": "",
        "location": "",
        "dimensions": "",
        "description": "",
    }

    lines = caption.split("\n")
    desc_lines = []
    first_meaningful = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detectar ano (4 dígitos isolados)
        year_match = re.match(r"^(\d{4})$", line)
        if year_match:
            info["year"] = year_match.group(1)
            continue

        # Detectar dimensões (padrões como 30cm x 50cm, 140cm x 200cm, etc.)
        dim_match = re.search(
            r"(\d+\s*(?:cm|m|px|pixels))\s*(?:[x×]\s*(\d+\s*(?:cm|m|px|pixels)))?",
            line,
            re.IGNORECASE,
        )
        if dim_match:
            info["dimensions"] = line
            continue

        # Detectar técnica
        tech_patterns = [
            "toma directa",
            "35mm",
            "nikon",
            "celular",
            "edição digital",
            "acrílico",
            "collage",
            "papel de seda",
            "superfícies sensibilizadas",
            "fotografía",
            "técnica",
            "acrilico",
            "cartapesta",
            "bambu",
        ]
        if any(p in line.lower() for p in tech_patterns):
            if not info["technique"]:
                info["technique"] = line
            else:
                desc_lines.append(line)
            continue

        # Detectar localização
        loc_patterns = [
            "argentina",
            "uruguay",
            "uruguai",
            "brasil",
            "chile",
            "buenos aires",
            "colonia",
            "corrientes",
            "garopaba",
            "florianópolis",
            "porto alegre",
            "grenoble",
            "köln",
            "alemanha",
            "alemania",
            "francia",
            "frança",
            "montevideo",
            "viña del mar",
            "salta",
            "neuquén",
            "mar del plata",
            "santa catarina",
            "bahia",
            "rancho29",
            "lutero bar",
            "casa escópica",
            "bahia blanca",
            "eterna cadencia",
            "bernin",
            "berlin",
            "köln",
            "colônia",
        ]
        if any(p in line.lower() for p in loc_patterns) and not info["location"]:
            info["location"] = line
            continue

        # Detectar título (primeira linha entre aspas)
        if not info["title"] and (line.startswith('"') or line.startswith('"')):
            info["title"] = line.strip('"').strip()
            if first_meaningful is None:
                first_meaningful = info["title"]
            continue

        # Detectar "Vendido"
        if line.lower() in ["vendido", "vendido."]:
            desc_lines.append(line)
            continue

        # Detectar série
        if (
            line.lower().startswith("serie")
            or line.lower().startswith("da serie")
            or line.lower().startswith("de la serie")
        ):
            if not info["title"]:
                info["title"] = line
            else:
                desc_lines.append(line)
            continue

        # Detectar menções a galerias/exposições
        gallery_patterns = [
            "galeria",
            "galerie",
            "exposição",
            "exposición",
            "photogalerie",
        ]
        if any(p in line.lower() for p in gallery_patterns):
            if not info["location"]:
                info["location"] = line
            else:
                desc_lines.append(line)
            continue

        # Detectar "Foto:" (crédito)
        if line.startswith("Foto:"):
            desc_lines.append(line)
            continue

        # Detectar menções a @
        if line.startswith("@"):
            desc_lines.append(line)
            continue

        # Linha genérica de descrição
        if len(line) > 2 and not line.startswith("#"):
            if first_meaningful is None:
                first_meaningful = line
            desc_lines.append(line)

    # Se não tem título, usar a primeira linha significativa
    if not info["title"] and first_meaningful:
        # Se a primeira linha é muito longa, não usar como título
        if len(first_meaningful) < 80:
            info["title"] = first_meaningful

    info["description"] = "\n".join(desc_lines)
    return info


def main():
    posts = []
    txt_files = sorted(GALERIA_DIR.glob("*.txt"))

    print(f"Encontrados {len(txt_files)} arquivos .txt")

    for txt_file in txt_files:
        caption = get_caption(txt_file)
        images = find_images_for_post(txt_file.name)

        if not images:
            continue  # Pula posts sem imagem

        info = extract_info(caption)

        post = {
            "id": txt_file.stem,
            "caption": caption,
            "images": images,
            "info": info,
            "date": txt_file.stem[:10],  # YYYY-MM-DD
        }
        posts.append(post)

    print(f"Posts com imagens: {len(posts)}")

    # Gerar HTML
    html_parts = []

    for i, post in enumerate(posts):
        img_src = post["images"][0]  # Primeira imagem
        info = post["info"]

        # Construir título - só mostra se houver título real do .txt, senão deixa vazio
        title = info["title"]

        # Escapar aspas para HTML (se houver título)
        title_escaped = title.replace('"', "&quot;") if title else ""

        # Construir metadados
        meta_parts = []
        if info["year"]:
            meta_parts.append(info["year"])
        if info["location"]:
            meta_parts.append(info["location"])
        if info["technique"]:
            meta_parts.append(info["technique"])
        if info["dimensions"]:
            meta_parts.append(info["dimensions"])

        meta_str = " · ".join(meta_parts) if meta_parts else ""

        # Descrição (sem hashtags, sem metadados já usados)
        desc = info["description"].strip()
        desc_escaped = desc.replace('"', "&quot;")

        html_parts.append(f'''          <div class="gallery-slide" data-index="{i}" data-date="{post["date"]}">
            <figure class="gallery-figure">
              <img src="images/{img_src}" alt="{title_escaped}" class="gallery-img" loading="lazy" />
              <figcaption class="gallery-caption">
                <h3 class="gallery-title">{title_escaped}</h3>
                {f'<p class="gallery-meta">{meta_str}</p>' if meta_str else ""}
                {f'<p class="gallery-desc">{desc_escaped}</p>' if desc else ""}
              </figcaption>
            </figure>
          </div>''')

    output = "\n\n".join(html_parts)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"HTML gerado em {OUTPUT_HTML}")
    print(f"Total de slides: {len(posts)}")


if __name__ == "__main__":
    main()
