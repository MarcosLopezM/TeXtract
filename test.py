import pymupdf
import re
import latexcodec
from prettyprinter import cpprint
from itertools import groupby
# import pandas as pd

doc = pymupdf.open(
    "./Matthew D. Schwartz - Quantum Field Theory And The Standard Model-Cambridge University Press (2014).pdf"
)

SPECIAL_LATEX_MAP = {
    "≡": r"\equiv ",
    "≥": r"\geq ",
    "≤": r"\leq ",
    "≈": r"\approx ",
    "→": r"\rightarrow ",
    "∞": r"\infty ",
}


def replace_special_chars(text):
    for k, v in SPECIAL_LATEX_MAP.items():
        text = text.replace(k, v)
    return text


# Función para convertir el texto extraído a LaTeX
def to_latex(text):
    text = replace_special_chars(text)
    return text.encode("latex", errors="replace").decode("utf-8")


toc = doc.get_toc(False)  # Extraer el TOC con detalles

# Filtramos el TOC para obtener las secciones con problemas
resultados = []
cur_level_1 = None
cur_level_2 = None

for i, item in enumerate(toc):
    level = item[0]
    title = item[1].strip()
    # page = int(item[3]["page"])

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

# Extraer los problemas
for chapter in resultados:
    # print(f"{chapter}")
    for section in resultados[chapter]:
        page_start = section["page_start"]
        page_end = section["page_end"]

        # print(f" Sección: {section['section']} -- {page_start}---{page_end}")

        section_title = section["section"]
        chapter_match = re.match(r"(?:Appendix\s+)?([A-Z]|\d+)", section_title)
        chapter_number = chapter_match.group(1) if chapter_match else "Sepa"

        problem_pattern = re.compile(rf"^\s*{chapter_number}[\.\-]\d+")
        inciso_pattern = re.compile(r"^\s*(?:[a-z]|\d+|i{1,3}|iv|v|vi{0,3}|ix|x)\)")

        all_problems_lines = []
        current_problem = ""
        inside_problem = False

        found_problems = False
        max_lookahead = 3

        for offset in range(0, max_lookahead + 1):
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
                        all_problems_lines.append(to_latex(current_problem.strip()))

                    current_problem = clean_line
                    inside_problem = True

                elif inside_problem:
                    if inciso_pattern.match(clean_line) or clean_line:
                        current_problem += "\n" + clean_line

        if inside_problem and current_problem:
            all_problems_lines.append(to_latex(current_problem.strip()))

        section["content"] = "\n\n".join(all_problems_lines)

cpprint(resultados)
