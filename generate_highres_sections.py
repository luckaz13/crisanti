#!/usr/bin/env python3
"""
Gera seções de alta resolução para o index.html, inspiradas na seção "Em foco Série Seda".
Cada pasta em /images/highres/ vira uma nova seção com galeria em carrossel.
"""

import os
from pathlib import Path

HIGHRES_DIR = Path("images/highres")
SERIE_NAMES = {
    "Der Elefant": "Der Elefant",
    "Juego del Tren": "Juego del Tren",
    "La Fuente y los Simios": "La Fuente y los Simios",
    "SEDA": "Seda",
    "SEDA 2024": "Seda 2024",
    "SEDA BAHIA": "Seda Bahia",
}

SERIE_DESCRIPTIONS = {
    "Der Elefant": "Na série Der Elefant, o artista explora a relação entre memória e figuração, trabalhando com técnicas mistas sobre papel de seda e superfícies industriais.",
    "Juego del Tren": "Juego del Tren apresenta uma reflexão sobre movimento, jogo e jornada, com composições que emergem do diálogo entre cores metálicas e texturas orgânicas.",
    "La Fuente y los Simios": "La Fuente y los Simios investiga a relação entre fonte (fonte de vida) e os seres simios, criando um universo onírinco de formas e significados.",
    "Seda": "Seda é uma série emblemática do artista, explorando a dialética entre arte contemporânea e tradição, entre origem e originalidade.",
    "Seda 2024": "Continuação da série Seda, apresentando novas explorações com técnicas atualizadas e composições contemporâneas.",
    "Seda Bahia": "Seda Bahia traz a série para o contexto baiano, dialogando com a paisagem e cultura local.",
}


def get_image_files(folder_path):
    """Get sorted list of image files (jpg, jpeg, png, webp) from folder."""
    extensions = {".jpg", ".jpeg", ".png", ".webp"}
    files = [f for f in os.listdir(folder_path) if Path(f).suffix.lower() in extensions]
    files.sort()
    return files


def generate_section(serie_key, serie_name):
    """Generate HTML section for a series folder."""
    folder_path = HIGHRES_DIR / serie_key
    if not folder_path.exists():
        return ""

    image_files = get_image_files(folder_path)
    if not image_files:
        return ""

    description = SERIE_DESCRIPTIONS.get(
        serie_name, f"Série {serie_name} - obras em alta resolução."
    )

    # Generate carousel slides
    slides_html = []
    for i, img in enumerate(image_files):
        img_path = f"images/highres/{serie_key}/{img}"
        slides_html.append(f'''            <div class="gallery-slide" data-index="{i}">
              <figure class="gallery-figure">
                <img src="{img_path}" alt="{serie_name} — Fabio Crisanti" class="gallery-img" loading="lazy" />
              </figure>
            </div>''')

    section_id = (
        serie_name.lower()
        .replace(" ", "-")
        .replace("ñ", "n")
        .replace("á", "a")
        .replace("í", "i")
        .replace("ó", "o")
    )

    html = f'''
    <!-- ═══════════════════════ {serie_name.upper()} ═══════════════════════ -->
    <section class="section series" id="{section_id}">
      <div class="container series-grid">
        <div class="series-text">
          <header class="section-header">
            <span class="section-label">Em foco</span>
            <h2 class="section-title">{serie_name}</h2>
          </header>
          <p class="series-lead">
            {description}
          </p>
          <p>
            Todas as imagens apresentadas em alta resolução, permitindo a apreciação dos detalhes e texturas características da técnica do artista.
          </p>
        </div>
        <div class="series-gallery">
          <div class="gallery-carousel" id="gallery-carousel-{section_id}">
            <div class="gallery-controls">
              <button class="gallery-btn gallery-btn--prev" id="gallery-prev-{section_id}" aria-label="Imagem anterior">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
              </button>
              <button class="gallery-btn gallery-btn--next" id="gallery-next-{section_id}" aria-label="Próxima imagem">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
              </button>
            </div>
            <div class="gallery-viewport">
              <div class="gallery-track">
{chr(10).join(slides_html)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>'''

    return html


def main():
    sections = []
    for folder_name in sorted(os.listdir(HIGHRES_DIR)):
        folder_path = HIGHRES_DIR / folder_name
        if folder_path.is_dir():
            serie_name = SERIE_NAMES.get(folder_name, folder_name)
            section_html = generate_section(folder_name, serie_name)
            if section_html:
                sections.append(section_html)

    output = "\n".join(sections)
    print(output)

    # Also save to file for reference
    with open("highres_sections.html", "w") as f:
        f.write(output)


if __name__ == "__main__":
    main()
