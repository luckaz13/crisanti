#!/usr/bin/env python3
"""Report unintended Spanish remaining in the rendered PT-BR page."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup, Comment


ALLOWED_ORIGINAL_TITLES = {
    "Der Elefant",
    "El Calendario",
    "El Ciervo",
    "El Nombre",
    "El Teléfono",
    "Juego del Tren",
    "La Cocina",
    "La Fuente y los Simios",
    "Seis Animales",
}

PHRASE_RULES = {
    "vista-general": r"\bvista\s+general\b",
    "detalle": r"\bdetalle(?:s)?\b",
    "boceto": r"\bboceto(?:s)?\b",
    "materiales": r"\bmateriales\b",
    "spanish-material": r"\b(?:madera|cartón|acero|alambre|piel|cuero|caja|gomaespuma|lana\s+natural|terciopelo|seda\s+salvaje|hilos\s+encerados)\b",
    "spanish-page-label": r"(?:^|(?<=\d))(?:tapa|contratapa)(?:$|(?=[A-ZÁÉÍÓÚ]))|\b(?:tapa\s+del|retiro\s+de\s+tapa|imágenes\s+del|páginas?\s+\d+\s+y|contratapa\s+de)\b",
    "spanish-production": r"\b(?:diseño\s+digital|copias\s+fotográficas|tomadas\s+de\s+la\s+serie|desde\s+la\s+serie|motivo:)\b",
    "mixed-conjunction": r"\b(?:papel\s+de\s+seda|acrílicos?)\s+y\s+(?:collage|cromía)\b",
    "spanish-editorial-label": r"(?:emulsión|lienzo|papeles\s+metalizados|hilos\s+de|corcho|proceso\s+de|gráficos\s+descriptivos|elementos\s+del|ilustraciones\s+de|estructuras\s+de|páginas\s+centrales|galería\s+del|plano\s+contrapicado)",
    "spanish-criticism": r"\b(?:jlb\s+siempre|esta\s+pieza|la\s+de\s+aquellos|es,\s+en\s+el|fotografía\s+y\s+escultura|queremos\s+creer|así\s+pendulamos|cuando\s+yo|ahora\s+creo|los\s+diseños|juliana\s+lee|es\s+un\s+goce|los\s+[“\"]mapas|son\s+como|en\s+la\s+ideografia|en\s+otra\s+variante|si\s+lo\s+rearm|brillante\s+investigación)\b",
}

SPANISH_PROSE_WORDS = {
    "así", "aunque", "también", "mientras", "desde", "hacia", "fue", "fueron", "han",
    "una", "unas", "unos", "sus", "nuestro", "nuestra", "nuestras", "nuestros",
    "sino", "siempre", "años", "ella", "ellos", "del", "las", "los", "y",
}


@dataclass
class Finding:
    text: str
    rules: list[str]


@dataclass
class AuditReport:
    findings: list[Finding] = field(default_factory=list)


def _is_allowed_title(text: str) -> bool:
    return text.strip().strip('“”"') in ALLOWED_ORIGINAL_TITLES


def find_spanish_residuals(texts: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[str] = set()
    for raw_text in texts:
        text = " ".join(raw_text.split())
        if not text or text in seen or _is_allowed_title(text):
            continue
        seen.add(text)
        rules = [name for name, pattern in PHRASE_RULES.items() if re.search(pattern, text, re.IGNORECASE)]
        if len(text) >= 70:
            words = set(re.findall(r"[a-záéíóúüñ]+", text.casefold()))
            if len(words & SPANISH_PROSE_WORDS) >= 5:
                rules.append("spanish-prose")
        if rules:
            findings.append(Finding(text=text, rules=rules))
    return findings


def audit_pt_br_html(path: Path) -> AuditReport:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    for element in soup(["script", "style"]):
        element.decompose()
    texts = [
        str(node)
        for node in soup.find_all(string=True)
        if not isinstance(node, Comment) and str(node).strip()
    ]
    for element in soup.find_all(True):
        for attribute in ("alt", "aria-label", "title"):
            value = element.get(attribute)
            if isinstance(value, str) and value.strip():
                texts.append(value)
    return AuditReport(findings=find_spanish_residuals(texts))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    report = audit_pt_br_html(args.path)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    raise SystemExit(1 if report.findings else 0)


if __name__ == "__main__":
    main()
