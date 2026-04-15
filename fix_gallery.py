#!/usr/bin/env python3
"""
Script to fix the gallery section in index.html by replacing
the incorrect trajectory content with the actual gallery items.
"""

import os
from pathlib import Path


def fix_gallery():
    # Paths
    index_path = Path(
        "/home/lucas/Projetos/cristanti/code_sandbox_light_7db1e7f9_1776125489/index.html"
    )
    gallery_items_path = Path(
        "/home/lucas/Projetos/cristanti/code_sandbox_light_7db1e7f9_1776125489/galeria-items.html"
    )

    # Read files
    with open(index_path, "r", encoding="utf-8") as f:
        index_lines = f.readlines()

    with open(gallery_items_path, "r", encoding="utf-8") as f:
        gallery_content = f.read()

    # Find the start and end markers
    start_marker = "<!-- GALERIA ITEMS START -->"
    end_marker = "</div><!-- /traj-cols -->"

    start_idx = None
    end_idx = None

    for i, line in enumerate(index_lines):
        if start_marker in line:
            start_idx = i
        if end_marker in line and start_idx is not None:
            end_idx = i
            break

    if start_idx is None or end_idx is None:
        print("Error: Could not find markers in index.html")
        return False

    print(f"Found start marker at line {start_idx}")
    print(f"Found end marker at line {end_idx}")

    # Build new content
    # Keep everything up to and including the start marker line
    # Then add the gallery content (properly indented)
    # Then keep everything from the end marker line onwards

    # The gallery content should be placed inside the gallery-track div
    # So we need to insert it after the start marker and before the end marker

    new_lines = []

    # Add everything before the gallery area (including the start marker line)
    new_lines.extend(index_lines[: start_idx + 1])

    # Add the gallery content with proper indentation
    # The gallery-track div is already indented with 3 spaces (6 spaces total?)
    # Looking at the file, it seems to be 3 tabs or 12 spaces?
    # Let's match the indentation of the surrounding divs

    # The gallery-viewport has 3 spaces, gallery-track has 6 spaces
    # So gallery items should have 9 spaces
    indent = " " * 9

    # Split gallery content into lines and re-indent
    gallery_lines = gallery_content.split("\n")
    indented_gallery_lines = []
    for line in gallery_lines:
        if line.strip():  # Only indent non-empty lines
            indented_gallery_lines.append(indent + line)
        else:
            indented_gallery_lines.append(line)  # Keep empty lines as is

    new_lines.extend(indented_gallery_lines)
    new_lines.append("")  # Add a blank line after gallery content

    # Add everything after the end marker
    new_lines.extend(index_lines[end_idx:])

    # Write back to file
    with open(index_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"Successfully replaced lines {start_idx + 1}-{end_idx} with gallery content")
    print(f"Gallery contains {len(gallery_lines)} lines")
    return True


if __name__ == "__main__":
    fix_gallery()
