import os
import re
from pathlib import Path
from typing import Dict, List


def sanitize_filename(name: str) -> str:
    """Convierte un título en un nombre de archivo/directorio seguro"""
    name = re.sub(r"[^a-zA-Z0-9\-_]", "_", name)
    name = name.lower()
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def create_directory_structure(
    base_path: Path, chapter_name: str, section_name: str
) -> Path:
    """Crea la estructura de directorios y devuelve la ruta al directorio de la sección"""
    if "appendix" in chapter_name.lower():
        chapter_dir = base_path / "appendix"
    else:
        chap_num = re.search(r"\d+", chapter_name)
        chap_dir_name = f"chapter{chap_num.group(0) if chap_num else sanitize_filename(chapter_name)}"
        chapter_dir = base_path / chap_dir_name

    sec_num = re.search(r"\d+", section_name)
    sec_dir_name = (
        f"section{sec_num.group(0) if sec_num else sanitize_filename(section_name)}"
    )
    section_dir = chapter_dir / sec_dir_name

    section_dir.mkdir(parents=True, exist_ok=True)
    return section_dir


def format_problems(content: str) -> str:
    """Formatea problemas con múltiples niveles de incisos"""
    problems = content.split("\n\n")
    formatted_problems = []

    for problem in problems:
        if not problem.strip():
            continue

        lines = problem.split("\n")
        problem_header = lines[0]
        problem_body = lines[1:]

        # Procesamiento de niveles anidados
        latex_output = []
        current_level = 0
        last_indent = -1

        latex_output.append(f"\\textbf{{{problem_header}}}")

        for line in problem_body:
            if not line.strip():
                continue

            # Detectar nivel de anidamiento
            indent_match = re.match(r"^(\s*)", line)
            indent = len(indent_match.group(1)) if indent_match else 0
            line_content = line.strip()

            # Detectar tipo de inciso
            item_match = re.match(r"^([a-z]|iv?x?|i{1,3}|iv|x)\)", line_content)
            roman_match = re.match(r"^\(([ivx]+)\)", line_content)
            numeric_match = re.match(r"^\((\d+)\)", line_content)

            if item_match:  # Inciso tipo a), b), etc.
                item_type = "alph"
                item_label = item_match.group(1)
                content_start = item_match.end()
            elif roman_match:  # Inciso tipo (i), (ii), etc.
                item_type = "roman"
                item_label = roman_match.group(1)
                content_start = roman_match.end()
            elif numeric_match:  # Inciso tipo (1), (2), etc.
                item_type = "arabic"
                item_label = numeric_match.group(1)
                content_start = numeric_match.end()
            else:
                # Texto normal, no es un inciso
                if (
                    latex_output
                    and latex_output[-1].strip()
                    and not latex_output[-1].strip().startswith(("\\end{", "\\begin{"))
                ):
                    latex_output[-1] += " " + line_content
                else:
                    latex_output.append(line_content)
                continue

            item_content = line_content[content_start:].strip()

            # Manejar cambios de nivel
            if indent > last_indent:
                latex_output.append(f"\\begin{{enumerate}}[label=\\{item_type}*)]")
                current_level += 1
            elif indent < last_indent:
                close_count = (last_indent - indent) // 4  # Asume 4 espacios por nivel
                for _ in range(close_count):
                    latex_output.append("\\end{enumerate}")
                    current_level -= 1

            latex_output.append(f"    \\item {item_content}")
            last_indent = indent

        # Cerrar todos los niveles abiertos
        for _ in range(current_level):
            latex_output.append("\\end{enumerate}")

        formatted_problems.append("\n".join(latex_output))

    return "\n\n\\bigskip\n\n".join(formatted_problems)


def generate_section_tex(
    section_dir: Path, chapter_title: str, section_title: str, content: str
) -> None:
    """Genera el archivo section.tex con problemas formateados"""
    tex_content = f"""\\section{{{section_title}}}
% Problemas extraídos de: {chapter_title}

{format_problems(content)}
"""
    with open(section_dir / "section.tex", "w", encoding="utf-8") as f:
        f.write(tex_content)


def generate_main_tex(base_path: Path, chapter_data: Dict[str, List]) -> None:
    """Genera el archivo main.tex con las inclusiones automáticas"""
    includes = []
    chapter_counter = 1

    # Procesar capítulos normales
    for chapter, sections in chapter_data.items():
        if "appendix" in chapter.lower():
            continue

        includes.append(f"\\chapter{{{chapter}}}")

        for section in sections:
            sec_dir = create_directory_structure(
                base_path / "chapters", chapter, section["section"]
            )
            rel_path = (sec_dir / "section").relative_to(base_path).with_suffix("")
            includes.append(f"\\input{{{str(rel_path).replace(os.sep, '/')}}}")

        chapter_counter += 1

    # Procesar apéndices
    appendices = [chap for chap in chapter_data.keys() if "appendix" in chap.lower()]
    if appendices:
        includes.append("\n\\appendix")
        for app in sorted(
            appendices,
            key=lambda x: re.search(r"[A-Z]", x).group()
            if re.search(r"[A-Z]", x)
            else "",
        ):
            includes.append(f"\\chapter{{{app}}}")
            for section in chapter_data[app]:
                sec_dir = create_directory_structure(
                    base_path / "chapters", app, section["section"]
                )
                rel_path = sec_dir.relative_to(base_path).with_suffix("")
                includes.append(f"\\input{{{str(rel_path).replace(os.sep, '/')}}}")

    main_tex = f"""\\documentclass{{book}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath, amssymb, amsthm}}
\\usepackage{{graphicx}}
\\usepackage{{enumitem}}
\\usepackage{{parskip}}
\\usepackage{{titlesec}}

\\title{{Problemas de Quantum Field Theory And The Standard Model}}
\\author{{Extraídos automáticamente}}

\\setlist{{  
  topsep=0pt,
  itemsep=0pt,
  parsep=0pt,
  leftmargin=15pt,
  labelsep=5pt,
  labelwidth=15pt
}}

\\titleformat{{\\section}}
  {{\\normalfont\\large\\bfseries}}
  {{}}
  {{0pt}}
  {{}}

\\begin{{document}}

\\maketitle
\\tableofcontents

{"\n".join(includes)}

\\end{{document}}
"""
    with open(base_path / "main.tex", "w", encoding="utf-8") as f:
        f.write(main_tex)


def generate_latex_project(
    resultados: Dict[str, List], book_name: str = "Quantum_Field_Theory_Problems"
) -> None:
    """Función principal que genera todo el proyecto LaTeX"""
    base_path = Path(book_name)

    # Crear estructura base
    (base_path / "figs").mkdir(parents=True, exist_ok=True)
    chapters_path = base_path / "chapters"
    chapters_path.mkdir(exist_ok=True)

    # Generar estructura para cada capítulo/sección
    for chapter, sections in resultados.items():
        for section in sections:
            section_dir = create_directory_structure(
                chapters_path, chapter, section["section"]
            )
            generate_section_tex(
                section_dir, chapter, section["section"], section["content"]
            )

    # Generar archivos principales
    generate_main_tex(base_path, resultados)

    # Generar .gitignore
    with open(base_path / ".gitignore", "w") as f:
        f.write("""*.aux
*.log
*.out
*.toc
*.pdf
*.bbl
*.blg
*.fdb_latexmk
*.fls
*.synctex.gz
build/
""")

    print(f"Proyecto LaTeX generado en: {base_path.absolute()}")
