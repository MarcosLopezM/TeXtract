import pymupdf
import os
import re
import json
from itertools import groupby

doc = pymupdf.open(
    "./Matthew D. Schwartz - Quantum Field Theory And The Standard Model-Cambridge University Press (2014).pdf"
)

output_folder = "./figs/"
os.makedirs(output_folder, exist_ok=True)

toc = doc.get_toc(False)  # Extraer el TOC con detalles

# Filtramos el TOC para obtener las secciones con problemas
resultados = []
cur_level_1 = None
cur_level_2 = None

for i, item in enumerate(toc):
    level = item[0]
    title = item[1].strip()

    if level == 1 and (title.startswith("Part") or title.startswith("Appendices")):
        cur_level_1 = title
        cur_level_2 = None
    elif level == 2:
        cur_level_2 = title
    elif level == 3 and title == "Problems":
        page = int(item[3]["page"])
        if cur_level_1 is not None:
            if i + 1 < len(toc):
                next_page = int(toc[i + 1][3]["page"]) - 1
            else:
                next_page = len(doc) - 1

            resultados.append(
                {
                    "chapter": cur_level_1,
                    "section": cur_level_2,
                    "title": title,
                    "page_start": page,
                    "page_end": next_page,
                }
            )

# Agrupamos los resultados por capítulo
resultados = {
    key: list(group) for key, group in groupby(resultados, key=lambda x: x["chapter"])
}

# Eliminamos el campo "chapter" para mejorar la claridad
for chapter, sections in resultados.items():
    for i in range(len(sections)):
        del sections[i]["chapter"]  # Remove chapter key from sections

# Extraer los problemas y las imágenes en un solo bucle
for chapter in resultados:
    for section in resultados[chapter]:
        page_start = section["page_start"]
        page_end = section["page_end"]
        section_title = section["section"]
        title = section.get("title", "")

        # --------- Extracción de texto de problemas ---------
        chapter_match = re.match(r"(?:Appendix\s+)?([A-Z]|\d+)", section_title)
        chapter_number = chapter_match.group(1) if chapter_match else ""

        problem_pattern = re.compile(rf"^\s*{chapter_number}[\.\-]\d+")
        inciso_pattern = re.compile(r"^\s*(?:[a-z]|\d+|i{1,3}|iv|v|vi{0,3}|ix|x)\)")

        all_problems_lines = []
        current_problem = ""
        inside_problem = False

        found_problems = False
        max_lookahead = 3

        for offset in range(0, max_lookahead):
            current_page = page_start + offset
            if current_page > page_end or current_page >= len(doc):
                break

            page_text = doc[current_page].get_text()
            lines = page_text.split("\n")

            for line in lines:
                clean_line = line.strip()

                if problem_pattern.match(clean_line):
                    found_problems = True

                    if inside_problem and current_problem:
                        all_problems_lines.append(current_problem.strip())

                    current_problem = clean_line
                    inside_problem = True

                elif inside_problem:
                    if inciso_pattern.match(clean_line) or clean_line:
                        current_problem += "\n" + clean_line

        if inside_problem and current_problem:
            all_problems_lines.append(current_problem.strip())

        section["content"] = "\n\n".join(all_problems_lines)

        section["section"] = "_".join(section_title.split())

        # --------- Extracción de imágenes si es sección Problems ---------
        if title == "Problems":
            print(
                f"Extrayendo imágenes de '{section_title}' ({page_start} a {page_end})"
            )
            start = page_start
            end = page_end

            for page_number in range(start, end):
                page = doc.load_page(page_number)

                matrix = pymupdf.Matrix(2, 2)
                pix = page.get_pixmap()

                # Nombre de archivo
                section_title = section.get("section", "Unknown_Section")
                safe_section_name = (
                    str(section_title).replace(" ", "_").replace("/", "_")
                )
                image_filename = f"{safe_section_name}_page_{page_number + 1}.png"
                image_path = os.path.join(output_folder, image_filename)
                section["image_path"] = image_path

                # Guardar imagen
                pix.save(image_path)

# Exportar los resultados a un archivo JSON
with open("resultados.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)
